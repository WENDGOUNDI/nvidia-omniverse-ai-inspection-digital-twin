import random

import omni.ext
import omni.ui as ui
import omni.usd
import omni.kit.app

from pxr import UsdGeom, Gf


class DigitalTwinExtension(omni.ext.IExt):

    # =============================================================
    # EXTENSION STARTUP
    # =============================================================
    def on_startup(self, ext_id):

        print("Digital Twin Extension Started")

        # ---------------------------------------------------------
        # Conveyor / simulation settings
        # ---------------------------------------------------------

        # Y is UP in our current stage.
        # X = conveyor movement direction
        # Y = vertical direction
        # Z = conveyor width direction

        self._start_x = -250.0
        self._end_x = 250.0

        # Inspection gate center
        self._inspection_x = 100.0

        # Product movement speed
        self._speed = 40.0

        # Simulated AI inspection duration
        self._inspection_duration = 1.0

        # ---------------------------------------------------------
        # Product state
        # ---------------------------------------------------------

        self._product_x = self._start_x

        self._running = False

        self._inspecting = False

        self._inspection_done = False

        self._inspection_timer = 0.0

        self._last_result = "Not Inspected"

        # ---------------------------------------------------------
        # USD references
        # ---------------------------------------------------------

        self._product_translate_op = None

        self._product_color_attr = None

        # ---------------------------------------------------------
        # Production statistics
        # ---------------------------------------------------------

        self._total_count = 0
        self._ok_count = 0
        self._ng_count = 0

        # ---------------------------------------------------------
        # Omniverse update loop
        # ---------------------------------------------------------

        self._update_subscription = (
            omni.kit.app.get_app()
            .get_update_event_stream()
            .create_subscription_to_pop(
                self._on_update,
                name="DigitalTwinUpdate"
            )
        )

        # =========================================================
        # USER INTERFACE
        # =========================================================

        self._window = ui.Window(
            "Abdoul Digital Twin",
            width=380,
            height=520
        )

        with self._window.frame:

            with ui.VStack(spacing=8):

                ui.Label(
                    "Factory Conveyor Digital Twin",
                    height=30
                )

                ui.Separator()

                # -------------------------------------------------
                # Factory controls
                # -------------------------------------------------

                ui.Button(
                    "Create Factory",
                    height=40,
                    clicked_fn=self.create_factory
                )

                ui.Button(
                    "Start Conveyor",
                    height=40,
                    clicked_fn=self.start_conveyor
                )

                ui.Button(
                    "Stop Conveyor",
                    height=40,
                    clicked_fn=self.stop_conveyor
                )

                ui.Button(
                    "Reset Product",
                    height=40,
                    clicked_fn=self.reset_product
                )

                ui.Separator()

                # -------------------------------------------------
                # Runtime status
                # -------------------------------------------------

                self._status_label = ui.Label(
                    "Status: Waiting",
                    height=25
                )

                self._position_label = ui.Label(
                    "Product Position X: --",
                    height=25
                )

                self._inspection_label = ui.Label(
                    "Inspection Result: Not Inspected",
                    height=25
                )

                ui.Separator()

                ui.Label(
                    "Inspection Statistics",
                    height=25
                )

                self._total_label = ui.Label(
                    "Total Inspected: 0",
                    height=22
                )

                self._ok_label = ui.Label(
                    "OK: 0",
                    height=22
                )

                self._ng_label = ui.Label(
                    "NG: 0",
                    height=22
                )

                self._yield_label = ui.Label(
                    "Yield: 0.0%",
                    height=22
                )

                ui.Separator()

                ui.Button(
                    "Reset Statistics",
                    height=35,
                    clicked_fn=self.reset_statistics
                )

    # =============================================================
    # COLOR HELPER
    # =============================================================
    def set_color(self, prim, color):

        gprim = UsdGeom.Gprim(
            prim.GetPrim()
        )

        color_attr = gprim.GetDisplayColorAttr()

        if not color_attr:
            color_attr = (
                gprim.CreateDisplayColorAttr()
            )

        color_attr.Set(
            [
                Gf.Vec3f(
                    color[0],
                    color[1],
                    color[2]
                )
            ]
        )

        return color_attr

    # =============================================================
    # GENERIC BOX CREATOR
    #
    # IMPORTANT:
    # Translate is created BEFORE Scale.
    #
    # This keeps our objects properly aligned.
    # =============================================================
    def create_box(
        self,
        stage,
        path,
        position,
        scale,
        color
    ):

        box = UsdGeom.Cube.Define(
            stage,
            path
        )

        box.CreateSizeAttr(1.0)

        xform = UsdGeom.Xformable(
            box
        )

        # ---------------------------------------------------------
        # Translation
        # ---------------------------------------------------------

        translate_op = (
            xform.AddTranslateOp()
        )

        translate_op.Set(
            Gf.Vec3d(
                position[0],
                position[1],
                position[2]
            )
        )

        # ---------------------------------------------------------
        # Scale
        # ---------------------------------------------------------

        scale_op = (
            xform.AddScaleOp()
        )

        scale_op.Set(
            Gf.Vec3f(
                scale[0],
                scale[1],
                scale[2]
            )
        )

        # ---------------------------------------------------------
        # Color
        # ---------------------------------------------------------

        color_attr = self.set_color(
            box,
            color
        )

        return (
            box,
            translate_op,
            color_attr
        )

    # =============================================================
    # CREATE FACTORY
    # =============================================================
    def create_factory(self):

        stage = (
            omni.usd
            .get_context()
            .get_stage()
        )

        if stage is None:

            print(
                "No USD stage available."
            )

            return

        # ---------------------------------------------------------
        # Stop existing simulation first
        # ---------------------------------------------------------

        self._running = False
        self._inspecting = False

        self._product_translate_op = None
        self._product_color_attr = None

        # ---------------------------------------------------------
        # Remove previous factory
        # ---------------------------------------------------------

        if stage.GetPrimAtPath(
            "/World/Factory"
        ).IsValid():

            stage.RemovePrim(
                "/World/Factory"
            )

        # =========================================================
        # FACTORY ROOT
        # =========================================================

        UsdGeom.Xform.Define(
            stage,
            "/World/Factory"
        )

        # =========================================================
        # CONVEYOR BASE
        # =========================================================

        self.create_box(

            stage,

            "/World/Factory/ConveyorBase",

            position=(
                0.0,
                0.0,
                0.0
            ),

            scale=(
                700.0,
                20.0,
                160.0
            ),

            color=(
                0.15,
                0.15,
                0.15
            )
        )

        # =========================================================
        # LEFT RAIL
        # =========================================================

        self.create_box(

            stage,

            "/World/Factory/LeftRail",

            position=(
                0.0,
                30.0,
                -85.0
            ),

            scale=(
                700.0,
                40.0,
                8.0
            ),

            color=(
                0.30,
                0.30,
                0.30
            )
        )

        # =========================================================
        # RIGHT RAIL
        # =========================================================

        self.create_box(

            stage,

            "/World/Factory/RightRail",

            position=(
                0.0,
                30.0,
                85.0
            ),

            scale=(
                700.0,
                40.0,
                8.0
            ),

            color=(
                0.30,
                0.30,
                0.30
            )
        )

        # =========================================================
        # ROLLERS
        # =========================================================

        UsdGeom.Xform.Define(
            stage,
            "/World/Factory/Rollers"
        )

        roller_positions = [

            -300,
            -250,
            -200,
            -150,
            -100,
            -50,

            0,

            50,
            100,
            150,
            200,
            250,
            300
        ]

        for i, x_position in enumerate(
            roller_positions
        ):

            roller = (
                UsdGeom.Cylinder.Define(
                    stage,
                    f"/World/Factory/Rollers/Roller_{i:02d}"
                )
            )

            roller.CreateRadiusAttr(
                12.0
            )

            roller.CreateHeightAttr(
                150.0
            )

            # Roller spans Z direction
            roller.CreateAxisAttr(
                "Z"
            )

            roller_xform = (
                UsdGeom.Xformable(
                    roller
                )
            )

            roller_xform.AddTranslateOp().Set(

                Gf.Vec3d(

                    x_position,
                    20.0,
                    0.0
                )
            )

            self.set_color(

                roller,

                (
                    0.55,
                    0.55,
                    0.55
                )
            )

        # =========================================================
        # PRODUCT
        #
        # Orange = not inspected
        # Green  = OK
        # Red    = NG
        # =========================================================

        (
            product,
            self._product_translate_op,
            self._product_color_attr

        ) = self.create_box(

            stage,

            "/World/Factory/Product",

            position=(

                self._start_x,
                70.0,
                0.0
            ),

            scale=(
                70.0,
                70.0,
                70.0
            ),

            # Orange / yellow
            color=(
                1.0,
                0.55,
                0.05
            )
        )

        self._product_x = (
            self._start_x
        )

        # =========================================================
        # INSPECTION STATION
        # =========================================================

        UsdGeom.Xform.Define(

            stage,

            "/World/Factory/InspectionStation"
        )

        # ---------------------------------------------------------
        # Left post
        # ---------------------------------------------------------

        self.create_box(

            stage,

            "/World/Factory/InspectionStation/LeftPost",

            position=(
                self._inspection_x,
                100.0,
                -110.0
            ),

            scale=(
                20.0,
                180.0,
                20.0
            ),

            color=(
                0.05,
                0.20,
                0.90
            )
        )

        # ---------------------------------------------------------
        # Right post
        # ---------------------------------------------------------

        self.create_box(

            stage,

            "/World/Factory/InspectionStation/RightPost",

            position=(
                self._inspection_x,
                100.0,
                110.0
            ),

            scale=(
                20.0,
                180.0,
                20.0
            ),

            color=(
                0.05,
                0.20,
                0.90
            )
        )

        # ---------------------------------------------------------
        # Top beam
        # ---------------------------------------------------------

        self.create_box(

            stage,

            "/World/Factory/InspectionStation/TopBeam",

            position=(
                self._inspection_x,
                190.0,
                0.0
            ),

            scale=(
                25.0,
                20.0,
                240.0
            ),

            color=(
                0.05,
                0.20,
                0.90
            )
        )

        # ---------------------------------------------------------
        # Simulated inspection camera
        # ---------------------------------------------------------

        self.create_box(

            stage,

            "/World/Factory/InspectionStation/Camera",

            position=(
                self._inspection_x,
                155.0,
                0.0
            ),

            scale=(
                35.0,
                25.0,
                35.0
            ),

            color=(
                0.05,
                0.05,
                0.05
            )
        )

        # =========================================================
        # INITIAL PRODUCT STATE
        # =========================================================

        self._running = False

        self._inspecting = False

        self._inspection_done = False

        self._inspection_timer = 0.0

        self._last_result = (
            "Not Inspected"
        )

        self._status_label.text = (
            "Status: Factory Created"
        )

        self._position_label.text = (
            f"Product Position X: "
            f"{self._product_x:.1f}"
        )

        self._inspection_label.text = (
            "Inspection Result: "
            "Not Inspected"
        )

        print(
            "Factory successfully created."
        )

    # =============================================================
    # START CONVEYOR
    # =============================================================
    def start_conveyor(self):

        if self._product_translate_op is None:

            self._status_label.text = (
                "Status: Create Factory First"
            )

            print(
                "Create the factory first."
            )

            return

        # ---------------------------------------------------------
        # Product already reached end:
        # automatically start a new cycle
        # ---------------------------------------------------------

        if self._product_x >= self._end_x:

            self._prepare_new_product()

        self._running = True

        if not self._inspecting:

            self._status_label.text = (
                "Status: Conveyor Running"
            )

        print(
            "Conveyor started."
        )

    # =============================================================
    # STOP CONVEYOR
    # =============================================================
    def stop_conveyor(self):

        self._running = False

        if self._inspecting:

            self._status_label.text = (
                "Status: Inspection Paused"
            )

        else:

            self._status_label.text = (
                "Status: Conveyor Stopped"
            )

        print(
            "Conveyor stopped."
        )

    # =============================================================
    # RESET PRODUCT
    # =============================================================
    def reset_product(self):

        if self._product_translate_op is None:

            return

        self._running = False

        self._prepare_new_product()

        self._status_label.text = (
            "Status: Product Reset"
        )

        print(
            "Product reset."
        )

    # =============================================================
    # PREPARE PRODUCT FOR NEW CYCLE
    # =============================================================
    def _prepare_new_product(self):

        self._product_x = (
            self._start_x
        )

        self._inspection_done = False

        self._inspecting = False

        self._inspection_timer = 0.0

        self._last_result = (
            "Not Inspected"
        )

        # ---------------------------------------------------------
        # Reset product position
        # ---------------------------------------------------------

        if self._product_translate_op:

            self._product_translate_op.Set(

                Gf.Vec3d(

                    self._product_x,
                    70.0,
                    0.0
                )
            )

        # ---------------------------------------------------------
        # Return product to orange
        # ---------------------------------------------------------

        self._set_product_color(

            (
                1.0,
                0.55,
                0.05
            )
        )

        # ---------------------------------------------------------
        # Update UI
        # ---------------------------------------------------------

        if self._position_label:

            self._position_label.text = (

                f"Product Position X: "
                f"{self._product_x:.1f}"
            )

        if self._inspection_label:

            self._inspection_label.text = (

                "Inspection Result: "
                "Not Inspected"
            )

    # =============================================================
    # SET PRODUCT COLOR
    # =============================================================
    def _set_product_color(
        self,
        color
    ):

        if self._product_color_attr is None:

            return

        self._product_color_attr.Set(

            [
                Gf.Vec3f(

                    color[0],
                    color[1],
                    color[2]
                )
            ]
        )

    # =============================================================
    # BEGIN INSPECTION
    # =============================================================
    def _begin_inspection(self):

        self._inspecting = True

        self._inspection_timer = 0.0

        # Lock product exactly beneath inspection gate
        self._product_x = (
            self._inspection_x
        )

        self._product_translate_op.Set(

            Gf.Vec3d(

                self._product_x,
                70.0,
                0.0
            )
        )

        self._status_label.text = (
            "Status: AI Inspection..."
        )

        self._inspection_label.text = (
            "Inspection Result: Inspecting..."
        )

        print(
            "Product entered inspection station."
        )

    # =============================================================
    # COMPLETE RANDOM INSPECTION
    # =============================================================
    def _complete_inspection(self):

        # ---------------------------------------------------------
        # Random simulation
        #
        # Replace this later with a real AI model.
        # ---------------------------------------------------------

        result = random.choice(
            [
                "OK",
                "NG"
            ]
        )

        self._last_result = (
            result
        )

        self._total_count += 1

        # =========================================================
        # OK PRODUCT
        # =========================================================

        if result == "OK":

            self._ok_count += 1

            # Green
            self._set_product_color(

                (
                    0.05,
                    0.85,
                    0.15
                )
            )

            self._status_label.text = (
                "Status: Inspection Complete - OK"
            )

        # =========================================================
        # NG PRODUCT
        # =========================================================

        else:

            self._ng_count += 1

            # Red
            self._set_product_color(

                (
                    1.0,
                    0.05,
                    0.05
                )
            )

            self._status_label.text = (
                "Status: Inspection Complete - NG"
            )

        # ---------------------------------------------------------
        # Inspection completed
        # ---------------------------------------------------------

        self._inspection_done = True

        self._inspecting = False

        self._inspection_timer = 0.0

        self._inspection_label.text = (

            f"Inspection Result: "
            f"{result}"
        )

        self._update_statistics_ui()

        print(
            f"Inspection result: {result}"
        )

    # =============================================================
    # UPDATE STATISTICS UI
    # =============================================================
    def _update_statistics_ui(self):

        self._total_label.text = (
            f"Total Inspected: "
            f"{self._total_count}"
        )

        self._ok_label.text = (
            f"OK: "
            f"{self._ok_count}"
        )

        self._ng_label.text = (
            f"NG: "
            f"{self._ng_count}"
        )

        # ---------------------------------------------------------
        # Yield calculation
        # ---------------------------------------------------------

        if self._total_count > 0:

            yield_percentage = (

                self._ok_count
                /
                self._total_count
                *
                100.0
            )

        else:

            yield_percentage = 0.0

        self._yield_label.text = (

            f"Yield: "
            f"{yield_percentage:.1f}%"
        )

    # =============================================================
    # RESET STATISTICS
    # =============================================================
    def reset_statistics(self):

        self._total_count = 0
        self._ok_count = 0
        self._ng_count = 0

        self._update_statistics_ui()

        print(
            "Inspection statistics reset."
        )

    # =============================================================
    # UPDATE LOOP
    # =============================================================
    def _on_update(
        self,
        event
    ):

        # Conveyor must be active
        if not self._running:

            return

        if self._product_translate_op is None:

            return

        # ---------------------------------------------------------
        # Delta time
        # ---------------------------------------------------------

        dt = event.payload.get(
            "dt",
            0.0
        )

        if dt <= 0:

            return

        # =========================================================
        # PRODUCT CURRENTLY BEING INSPECTED
        # =========================================================

        if self._inspecting:

            self._inspection_timer += dt

            self._status_label.text = (

                "Status: AI Inspection... "
                f"{self._inspection_timer:.1f}s"
            )

            # ---------------------------------------------
            # Wait until inspection duration is reached
            # ---------------------------------------------

            if (
                self._inspection_timer
                >=
                self._inspection_duration
            ):

                self._complete_inspection()

            # Product does not move while inspecting
            return

        # =========================================================
        # MOVE PRODUCT
        # =========================================================

        self._product_x += (
            self._speed * dt
        )

        # =========================================================
        # CHECK INSPECTION ZONE
        # =========================================================

        if (
            not self._inspection_done
            and
            self._product_x
            >=
            self._inspection_x
        ):

            self._begin_inspection()

            return

        # =========================================================
        # END OF CONVEYOR
        # =========================================================

        if (
            self._product_x
            >=
            self._end_x
        ):

            self._product_x = (
                self._end_x
            )

            self._running = False

            self._status_label.text = (
                "Status: Product Reached End"
            )

        # =========================================================
        # UPDATE PRODUCT POSITION
        # =========================================================

        self._product_translate_op.Set(

            Gf.Vec3d(

                self._product_x,
                70.0,
                0.0
            )
        )

        # =========================================================
        # UPDATE POSITION UI
        # =========================================================

        self._position_label.text = (

            f"Product Position X: "
            f"{self._product_x:.1f}"
        )

    # =============================================================
    # EXTENSION SHUTDOWN
    # =============================================================
    def on_shutdown(self):

        print(
            "Digital Twin Extension Shutdown"
        )

        self._running = False

        self._inspecting = False

        self._update_subscription = None

        self._product_translate_op = None

        self._product_color_attr = None

        self._window = None