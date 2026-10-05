import omni.ext
import omni.ui as ui
import omni.usd
import omni.kit.app

from pxr import UsdGeom, Gf


class DigitalTwinExtension(omni.ext.IExt):

    def on_startup(self, ext_id):
        print("Digital Twin Extension Started")

        # =========================================================
        # SIMULATION SETTINGS
        # =========================================================

        self._running = False

        # X = conveyor movement
        # Y = vertical axis
        # Z = conveyor width
        self._start_x = -250.0
        self._end_x = 250.0
        self._product_x = self._start_x

        self._speed = 40.0

        self._product_translate_op = None

        # =========================================================
        # UPDATE LOOP
        # =========================================================

        self._update_subscription = (
            omni.kit.app.get_app()
            .get_update_event_stream()
            .create_subscription_to_pop(
                self._on_update,
                name="DigitalTwinUpdate"
            )
        )

        # =========================================================
        # UI
        # =========================================================

        self._window = ui.Window(
            "Abdoul Digital Twin",
            width=360,
            height=360
        )

        with self._window.frame:

            with ui.VStack(spacing=10):

                ui.Label(
                    "Factory Conveyor Digital Twin",
                    height=30
                )

                ui.Separator()

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

                self._status_label = ui.Label(
                    "Status: Waiting",
                    height=30
                )

                self._position_label = ui.Label(
                    "Product Position: --",
                    height=30
                )

    # =============================================================
    # HELPER: COLOR
    # =============================================================

    def set_color(self, prim, color):

        gprim = UsdGeom.Gprim(
            prim.GetPrim()
        )

        gprim.CreateDisplayColorAttr(
            [
                Gf.Vec3f(
                    color[0],
                    color[1],
                    color[2]
                )
            ]
        )

    # =============================================================
    # HELPER: CREATE BOX
    #
    # IMPORTANT:
    # Translate is created BEFORE Scale.
    # This avoids the alignment problem we had previously.
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

        xform = UsdGeom.Xformable(box)

        # IMPORTANT:
        # translation first
        translate_op = xform.AddTranslateOp()

        translate_op.Set(
            Gf.Vec3d(
                position[0],
                position[1],
                position[2]
            )
        )

        # scale second
        scale_op = xform.AddScaleOp()

        scale_op.Set(
            Gf.Vec3f(
                scale[0],
                scale[1],
                scale[2]
            )
        )

        self.set_color(
            box,
            color
        )

        return box, translate_op

    # =============================================================
    # CREATE FACTORY
    # =============================================================

    def create_factory(self):

        stage = omni.usd.get_context().get_stage()

        if stage is None:

            print("No USD stage available")

            return

        # =========================================================
        # REMOVE OLD FACTORY
        # =========================================================

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
        #
        # X = 700 length
        # Y = 20 height
        # Z = 160 width
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
        # ROLLERS ROOT
        # =========================================================

        UsdGeom.Xform.Define(
            stage,
            "/World/Factory/Rollers"
        )

        # =========================================================
        # ROLLERS
        # =========================================================

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

            roller = UsdGeom.Cylinder.Define(

                stage,

                f"/World/Factory/Rollers/Roller_{i:02d}"
            )

            roller.CreateRadiusAttr(
                12.0
            )

            roller.CreateHeightAttr(
                150.0
            )

            # Cylinder spans conveyor width
            roller.CreateAxisAttr(
                "Z"
            )

            roller_xform = UsdGeom.Xformable(
                roller
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
        # =========================================================

        product, self._product_translate_op = (
            self.create_box(

                stage,

                "/World/Factory/Product",

                position=(

                    self._start_x,

                    # Product sits on top
                    # of conveyor rollers
                    70.0,

                    0.0
                ),

                scale=(
                    70.0,
                    70.0,
                    70.0
                ),

                # Bright RED
                color=(
                    1.0,
                    0.05,
                    0.05
                )
            )
        )

        self._product_x = (
            self._start_x
        )

        # =========================================================
        # INSPECTION STATION ROOT
        # =========================================================

        UsdGeom.Xform.Define(

            stage,

            "/World/Factory/InspectionStation"
        )

        # =========================================================
        # INSPECTION STATION LEFT POST
        # =========================================================

        self.create_box(

            stage,

            "/World/Factory/InspectionStation/LeftPost",

            position=(
                100.0,
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

        # =========================================================
        # INSPECTION STATION RIGHT POST
        # =========================================================

        self.create_box(

            stage,

            "/World/Factory/InspectionStation/RightPost",

            position=(
                100.0,
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

        # =========================================================
        # INSPECTION STATION TOP
        # =========================================================

        self.create_box(

            stage,

            "/World/Factory/InspectionStation/TopBeam",

            position=(
                100.0,
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

        # =========================================================
        # INSPECTION CAMERA
        # =========================================================

        self.create_box(

            stage,

            "/World/Factory/InspectionStation/Camera",

            position=(
                100.0,
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
        # STATE
        # =========================================================

        self._running = False

        self._status_label.text = (
            "Status: Factory Created"
        )

        self._position_label.text = (
            f"Product Position X: {self._product_x:.1f}"
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
        # If product already reached end,
        # return to start automatically
        # ---------------------------------------------------------

        if self._product_x >= self._end_x:

            self._product_x = (
                self._start_x
            )

            self._product_translate_op.Set(

                Gf.Vec3d(

                    self._product_x,
                    70.0,
                    0.0
                )
            )

        self._running = True

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

        self._product_x = (
            self._start_x
        )

        self._product_translate_op.Set(

            Gf.Vec3d(

                self._product_x,
                70.0,
                0.0
            )
        )

        self._status_label.text = (
            "Status: Product Reset"
        )

        self._position_label.text = (
            f"Product Position X: {self._product_x:.1f}"
        )

        print(
            "Product reset."
        )

    # =============================================================
    # UPDATE LOOP
    # =============================================================

    def _on_update(
        self,
        event
    ):

        if not self._running:

            return

        if self._product_translate_op is None:

            return

        # =========================================================
        # DELTA TIME
        # =========================================================

        dt = event.payload.get(
            "dt",
            0.0
        )

        if dt <= 0:

            return

        # =========================================================
        # UPDATE PRODUCT X
        # =========================================================

        self._product_x += (
            self._speed * dt
        )

        # =========================================================
        # END OF CONVEYOR
        # =========================================================

        if self._product_x >= self._end_x:

            self._product_x = (
                self._end_x
            )

            self._running = False

            self._status_label.text = (
                "Status: Product Reached End"
            )

        # =========================================================
        # UPDATE USD POSITION
        # =========================================================

        self._product_translate_op.Set(

            Gf.Vec3d(

                self._product_x,

                # Always stays above conveyor
                70.0,

                # Always centered
                0.0
            )
        )

        # =========================================================
        # UPDATE UI
        # =========================================================

        self._position_label.text = (

            f"Product Position X: "
            f"{self._product_x:.1f}"
        )

    # =============================================================
    # SHUTDOWN
    # =============================================================

    def on_shutdown(self):

        print(
            "Digital Twin Extension Shutdown"
        )

        self._running = False

        self._update_subscription = None

        self._product_translate_op = None

        self._window = None