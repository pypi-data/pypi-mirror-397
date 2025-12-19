# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import gevent
from bliss import global_map
from bliss.common import event
from bliss.common.greenlet_utils.killmask import BlissGreenlet
from bliss.config.static import ConfigNode
from bliss.controllers.motor import Controller
from bliss.common.axis import Motion, AxisState, lazy_init
from bliss.common.axis import Axis as BaseAxis


class SeqAxis(BaseAxis):
    @property
    def dial_limits(self) -> tuple[float, float]:
        raw_axis = self.controller._get_linked(self)
        return raw_axis.dial_limits

    @dial_limits.setter
    @lazy_init
    def dial_limits(self, limits: tuple[float, float]) -> None:
        raw_axis = self.controller._get_linked(self)
        raw_axis.dial_limits = limits

    @property
    def limits(self) -> tuple[float, float]:
        raw_axis = self.controller._get_linked(self)
        return raw_axis.limits

    @limits.setter
    def limits(self, limits: tuple[float, float]) -> None:
        raw_axis = self.controller._get_linked(self)
        raw_axis.limits = limits

    @property
    def low_limit(self) -> float:
        raw_axis = self.controller._get_linked(self)
        return raw_axis.low_limit

    @low_limit.setter
    @lazy_init
    def low_limit(self, limit: float) -> None:
        raw_axis = self.controller._get_linked(self)
        raw_axis.low_limit = limit

    @property
    def high_limit(self) -> float:
        raw_axis = self.controller._get_linked(self)
        return raw_axis.high_limit

    @high_limit.setter
    @lazy_init
    def high_limit(self, limit: float) -> None:
        raw_axis = self.controller._get_linked(self)
        raw_axis.high_limit = limit

    @property
    def config_limits(self) -> tuple[float, float]:
        raw_axis = self.controller._get_linked(self)
        return raw_axis.config_limits

    def sync_hard(self) -> None:
        raw_axis = self.controller._get_linked(self)
        raw_axis.sync_hard()
        super().sync_hard()

    def apply_config(
        self,
        reload=False,
        velocity=True,
        acceleration=True,
        limits=True,
        sign=True,
        backlash=True,
    ) -> None:

        raw_axis = self.controller._get_linked(self)
        raw_axis.apply_config(
            reload=reload,
            velocity=velocity,
            acceleration=acceleration,
            limits=limits,
            sign=sign,
            backlash=backlash,
        )


class Sequencer(Controller):

    """A controller to serialize the motions of the axes referenced in its configuration.
    It ensures that declared axes cannot be moved in parallel.

    YAML configuration example:

      - class: Sequencer
        plugin: emotion
        axes:
          - name: sax
            axis: $ax

          - name: say
            axis: $ay

          - name: saz
            axis: $az

    'sax' is the serialized version of 'ax'
    'say' is the serialized version of 'ay'
    'saz' is the serialized version of 'az'

    example:
        => move(sax, 1, say, 2)
        'sax' moves first to 1.
        'say' starts moving to 2 only when 'sax' has reached its target position.
        'saz' cannot be moved while motion command is running.
    """

    def _get_subitem_default_class_name(
        self, cfg: ConfigNode | dict, parent_key: str
    ) -> str:
        if parent_key == "axes":
            return "SeqAxis"
        else:
            return super()._get_subitem_default_class_name(cfg, parent_key)

    def _get_linked(self, axis: SeqAxis) -> BaseAxis:
        return axis.config.get("axis")

    def _perform_move_task(self, *motion_list: Motion) -> None:
        for motion in motion_list:
            linked_axis = self._get_linked(motion.axis)
            linked_axis.move(motion.user_target_pos)

    def _on_position_event(self, value: float, sender: BaseAxis) -> None:
        axis = self._raw2axis[sender]
        axis.settings.set(
            "dial_position", value, "position", axis.dial2user(value, axis.offset)
        )

    def _on_state_event(self, value: AxisState, sender: BaseAxis) -> None:
        self._raw2axis[sender].settings.set("state", value)

    def _on_set_position_event(self, value: float, sender: BaseAxis) -> None:
        self._raw2axis[sender].settings.set("_set_position", value)

    def initialize(self) -> None:
        self._raw2axis: dict[BaseAxis, SeqAxis] = {}
        self._move_task: BlissGreenlet | None = None
        global_map.register(self)

    def initialize_axis(self, axis: SeqAxis) -> None:
        linked_axis = axis.config.get("axis")
        if linked_axis is None:
            raise RuntimeError(f"missing key 'axis 'in {axis.name} YAML configuration")

        self._raw2axis[linked_axis] = axis
        axis.config.set("velocity", linked_axis.velocity)
        axis.config.set("acceleration", linked_axis.acceleration)
        axis.config.set("steps_per_unit", linked_axis.steps_per_unit)

        event.connect(linked_axis, "state", self._on_state_event)
        event.connect(linked_axis, "internal_position", self._on_position_event)
        event.connect(
            linked_axis, "internal__set_position", self._on_set_position_event
        )

    def close(self) -> None:
        for linked_axis in self._raw2axis:
            event.disconnect(linked_axis, "state", self._on_state_event)
            event.disconnect(linked_axis, "internal_position", self._on_position_event)
            event.disconnect(
                linked_axis, "internal__set_position", self._on_set_position_event
            )

    def prepare_all(self, *motion_list: Motion) -> None:
        raise NotImplementedError

    def prepare_move(self, motion: Motion) -> None:
        return None

    def start_one(self, motion: Motion) -> None:
        raise NotImplementedError

    def start_all(self, *motion_list: Motion) -> None:
        if self._move_task:
            raise RuntimeError(
                f"MotionSequencer is already running a motion with {[ax.name for ax in self._in_motion_axes]}"
            )

        self._in_motion_axes: list[SeqAxis] = [motion.axis for motion in motion_list]
        task = gevent.spawn(self._perform_move_task, *motion_list)
        task.name = f"Sequencer_perform_move_task_{self.name}"
        self._move_task = task

    def start_jog(self, axis: SeqAxis, velocity: float, direction: int) -> None:
        raise NotImplementedError

    def stop(self, axis: SeqAxis) -> None:
        if self._move_task and axis in self._in_motion_axes:
            self._move_task.kill()

    def stop_all(self, *motions: Motion) -> None:
        raise NotImplementedError

    def read_position(self, axis: SeqAxis) -> float:
        return self._get_linked(axis)._hw_position

    def state(self, axis: SeqAxis) -> AxisState:
        if self._move_task and axis in self._in_motion_axes:
            return AxisState("MOVING")
        else:
            return AxisState("READY")

    def read_velocity(self, axis: SeqAxis) -> float:
        return self._get_linked(axis).velocity

    def set_velocity(self, axis: SeqAxis, velocity: float) -> None:
        self._get_linked(axis).velocity = velocity

    def read_acceleration(self, axis: SeqAxis) -> float:
        return self._get_linked(axis).acceleration

    def set_acceleration(self, axis: SeqAxis, acceleration: float) -> None:
        self._get_linked(axis).acceleration = acceleration

    def set_off(self, axis: SeqAxis) -> None:
        pass

    def set_on(self, axis: SeqAxis) -> None:
        pass
