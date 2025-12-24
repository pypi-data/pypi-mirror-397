"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import tempfile as tmpf
import typing as h
from io import StringIO as io_string_t
from pathlib import Path as path_t

import numpy as nmpy
from daccuracy.config.csv_ import COL_SEPARATOR
from daccuracy.config.nicegui import NOTIFICATION_OPTIONS
from daccuracy.constant.measures import MEASURES_DESCRIPTIONS
from daccuracy.constant.nicegui import FOOTER, HEADER, STYLE
from daccuracy.constant.project import PROJECT_NAME
from daccuracy.main import ComputeAndOutputMeasures
from imageio.v2 import imsave
from nicegui import app as nice_app_t
from nicegui import events, ui
from PIL import Image as image_t
from skimage.io import imread

array_t = nmpy.ndarray


@d.dataclass(slots=True, repr=False, eq=False)
class app_t:
    folder: path_t | None = None
    anti_cache_counter: int = 0
    # Otherwise, caching (probably) prevents high-contrast image updates.
    #
    ground_truth_container: h.Any = None
    ground_truth_path: path_t | None = None
    ground_truth_name: h.Any = None
    detection_container: h.Any = None
    detection_path: path_t | None = None
    detection_name: h.Any = None
    #
    output_tabs: h.Any = None
    output_csv: path_t | None = None
    output_image: path_t | None = None
    output_csv_container: h.Any = None
    output_image_container: h.Any = None
    output_image_legend: h.Any = None

    def __post_init__(self) -> None:
        """"""
        folder_record = tmpf.TemporaryDirectory(delete=False)
        self.folder = path_t(folder_record.name)

        with ui.column().classes("main_container"):
            ui.html(HEADER, sanitize=False).classes("w-full")
            ui.separator()
            #
            with ui.grid(columns=2).classes("w-full"):
                ui.upload(
                    label="Ground-Truth",
                    auto_upload=True,
                    on_upload=lambda _: self.UploadAndDisplayInput(_, "g"),
                ).classes("w-full")
                ui.upload(
                    label="Detection",
                    auto_upload=True,
                    on_upload=lambda _: self.UploadAndDisplayInput(_, "d"),
                ).classes("w-full")
                self.ground_truth_container = ui.column().classes("w-full")
                self.detection_container = ui.column().classes("w-full")
                self.ground_truth_name = ui.label("<Ground-Truth>").classes(
                    "text-center"
                )
                self.detection_name = ui.label("<Detection>").classes("text-center")
            #
            ui.button(
                "Compute Accuracy Measures", on_click=self.ComputeAccuracy
            ).classes("w-full")
            #
            with ui.tabs().classes("w-full") as self.output_tabs:
                tab_csv = ui.tab("CSV")
                tab_image = ui.tab("Image")
                tab_definitions = ui.tab("Definitions")
            with ui.tab_panels(self.output_tabs, value=tab_definitions).classes(
                "w-full"
            ):
                with ui.tab_panel(tab_csv):
                    self.output_csv_container = ui.row().classes("w-full")
                    ui.button("Download CSV", on_click=self.DownloadCSV).classes(
                        "w-full"
                    )
                with ui.tab_panel(tab_image):
                    self.output_image_container = ui.row().classes("w-full")
                    self.output_image_legend = ui.label().classes("w-full text-center")
                    ui.button("Download Image", on_click=self.DownloadImage).classes(
                        "w-full"
                    )
                with ui.tab_panel(tab_definitions):
                    ui.markdown(content=MEASURES_DESCRIPTIONS).classes("w-full")
            #
            ui.separator()
            ui.html(FOOTER.format(self.folder), sanitize=False).classes("w-full")
            ui.separator()
            ui.button("Close App", on_click=self.Stop).classes("w-full")

    def Start(self) -> None:
        """"""
        ui.add_css(STYLE)
        ui.run(title=PROJECT_NAME, reload=False)

    async def Stop(self) -> None:
        """"""
        await ui.run_javascript("window.close()", timeout=0.1)
        nice_app_t.shutdown()

    def ComputeAccuracy(self, _: events.ClickEventArguments, /) -> None:
        """"""
        if (self.ground_truth_path is None) or (self.detection_path is None):
            return

        fake_file = io_string_t()
        options = {
            "ground_truth_path": self.ground_truth_path,
            "relabel_gt": None,
            "detection_path": self.detection_path,
            "relabel_dn": None,
            "coord_trans": None,
            "dn_shifts": None,
            "should_exclude_border": True,
            "tolerance": 0.0,
            "output_format": "csv",
            "should_return_image": True,
            "should_show_image": False,
            "output_accessor": fake_file,
        }

        image, n_correct, n_missed, n_invented = ComputeAndOutputMeasures(options)

        measures = fake_file.getvalue()
        fake_file.close()

        self.output_csv = self.folder / "daccuracy.csv"
        self.output_image = self.folder / "daccuracy.png"
        self.output_csv.write_text(measures)
        imsave(self.output_image, image)

        lines = []
        for line in measures.splitlines():
            lines.append(tuple(map(str.strip, line.split(COL_SEPARATOR))))
        header = lines[0]
        rows = [{__: ___ for __, ___ in zip(header, _, strict=True)} for _ in lines[1:]]
        with self.output_csv_container.clear():
            with ui.scroll_area().classes("w-full"):
                ui.table(rows=rows)

        image_pil = image_t.fromarray(image)
        with self.output_image_container.clear():
            ui.image(image_pil).on("click", self.DownloadImage).classes("w-1/2 m-auto")
        self.output_image_legend.set_text(
            f"Correct: {n_correct}, Missed: {n_missed}, Invented: {n_invented}"
        )

        self.output_tabs.set_value("CSV")

    async def UploadAndDisplayInput(
        self, args: events.UploadEventArguments, which: h.Literal["g", "d"], /
    ) -> None:
        """"""
        accessor = args.file

        if FileIsInvalid(accessor, which):
            return

        name_client = accessor.name
        extension = path_t(name_client).suffix

        if which == "g":
            name_server = "ground-truth"
        else:
            name_server = "detection"
        path_server = await self.UploadFile(accessor, name_server, extension)

        if which == "g":
            self.ground_truth_path = path_server
            name_visual = self.ground_truth_name
            file_visual = self.ground_truth_container
        else:
            self.detection_path = path_server
            name_visual = self.detection_name
            file_visual = self.detection_container

        name_visual.set_text(name_client)
        if accessor.content_type.startswith("image/"):
            try:
                image = imread(path_server)
            except:
                ui.notify("Unhandled Image Format", **NOTIFICATION_OPTIONS)
                return

            stretched = nmpy.around((255.0 / image.max()) * image).astype(nmpy.uint8)
            stretched = image_t.fromarray(stretched)
            with file_visual.clear():
                ui.image(stretched).classes("w-1/2 m-auto")
        else:
            with file_visual.clear():
                ui.markdown(content=f"{path_server.read_text()[:20]}\n[...]").classes(
                    "w-1/2 h-full m-auto"
                )

        await args.sender.run_method("reset")

    async def UploadFile(self, accessor: h.Any, name: str, extension: str, /) -> path_t:
        """
        extension: with dot.
        """
        for counter in range(self.anti_cache_counter):
            path = self.folder / f"{name}-{counter}{extension}"
            path.unlink(missing_ok=True)

        path = self.folder / f"{name}-{self.anti_cache_counter}{extension}"
        path.write_bytes(await accessor.read())

        self.anti_cache_counter += 1

        return path

    def DownloadCSV(self) -> None:
        """"""
        if self.output_csv is None:
            return

        ui.download.file(self.output_csv)

    def DownloadImage(self) -> None:
        """"""
        if self.output_image is None:
            return

        ui.download.file(self.output_image)


def FileIsInvalid(file: h.Any, which: str, /) -> bool:
    """"""
    file_is_image = file.content_type.startswith("image/")
    error_message = None
    if which == "g":
        if not (file_is_image or file.content_type.startswith("text/")):
            error_message = "Please upload an image or a CSV file"
    else:
        if not file_is_image:
            error_message = "Please upload an image file"

    if error_message is not None:
        ui.notify(error_message, **NOTIFICATION_OPTIONS)
        return True

    return False


def Main() -> None:
    """"""
    app = app_t()
    app.Start()


if __name__ in ("__main__", "__mp_main__"):
    #
    Main()
