"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dataclasses as d
import tempfile as tmpf
import typing as h
from pathlib import Path as path_t

import numpy as nmpy
import pca_b_stream.main as pcas
from nicegui import app as nice_app_t
from nicegui import events, ui
from pca_b_stream.constant import DETAILS_LEGEND, PROJECT_NAME
from pca_b_stream.nicegui.constant import (
    BYTE_STREAM_LENGTH_TEMPLATE,
    FOOTER,
    HEADER,
    PCA_SIZE_TEMPLATE,
    STYLE,
)
from skimage.io import imread, imsave

array_t = nmpy.ndarray


@d.dataclass(slots=True, repr=False, eq=False)
class app_t:
    folder: path_t | None = None
    path_decoded: path_t | None = None
    anti_cache_counter: int = 0
    # Otherwise, caching (probably) prevents high-contrast image updates.
    #
    pca_loader: h.Any = None
    pca_container: h.Any = None
    pca_name: h.Any = None
    pca_size: h.Any = None
    byte_stream: h.Any = None
    byte_stream_length: h.Any = None
    details_container: h.Any = None

    def __post_init__(self) -> None:
        """"""
        folder_record = tmpf.TemporaryDirectory(delete=False)
        self.folder = path_t(folder_record.name)

        with ui.column().classes("main_container"):
            ui.html(HEADER, sanitize=False).classes("w-full")
            # --- PCA Loading/Display.
            with ui.grid(columns=2).classes("w-full"):
                self.pca_loader = ui.upload(
                    label="Piecewise-Constant Array/Image",
                    auto_upload=True,
                    on_upload=self.ToByteStream,
                ).classes("w-full")
                self.pca_container = ui.column().classes("w-full")
                self.pca_name = ui.label("<Image Name>").classes("text-center")
                self.pca_size = ui.label("<Image Size>").classes("text-center")
            # --- Back-and-forth buttons.
            with ui.row().classes("w-full"):
                ui.button("↓ [Automatic]").classes("w-49/100").disable()
                ui.button("↑", on_click=self.ToPCA).classes("w-49/100")
            # --- Byte Stream Input/Display.
            with ui.row(align_items="center").classes("w-full flex"):
                self.byte_stream = (
                    ui.textarea(
                        label="Byte Stream", on_change=self._UpdateByteStreamLength
                    )
                    .classes("grow")
                    .props("clearable")
                )
                self.byte_stream_length = ui.label("<Byte Stream Length>").classes(
                    "flex-none"
                )
            self.details_container = ui.row()
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

    async def ToByteStream(self, args: events.UploadEventArguments, /) -> None:
        """"""
        if not args.file.content_type.startswith("image/"):
            ui.notify(
                "Please upload an image file", position="center", close_button=True
            )
            return

        path = self.folder / args.file.name
        path.write_bytes(await args.file.read())

        try:
            image = imread(path)
        except:
            ui.notify("Unhandled Image Format", position="center", close_button=True)
            return

        issues = pcas.PCArrayIssues(image)
        if issues.__len__() > 0:
            ui.notify(
                "\n".join(issues), position="center", close_button=True, multi_line=True
            )
            return

        stream = pcas.PCA2BStream(image)

        self._DisplayResults(stream, path.name, path.stat().st_size, image)
        await self.pca_loader.run_method("reset")

    def ToPCA(self, _: events.ClickEventArguments, /) -> None:
        """"""
        stream = bytes(self.byte_stream.value, "ascii")
        if stream.__len__() == 0:
            return

        try:
            decoded = pcas.BStream2PCA(stream)
        except:
            ui.notify("Invalid Stream", position="center", close_button=True)
            return

        self.path_decoded = self.folder / "pca.png"
        imsave(self.path_decoded, decoded)

        self._DisplayResults(stream, "<From Byte Stream>", -1, decoded)

    def _DisplayResults(
        self, stream: bytes, name: str, size: int, image: array_t, /
    ) -> None:
        """"""
        try:
            details = pcas.BStreamDetails(stream)
        except:
            ui.notify("Invalid Stream", position="center", close_button=True)
            return

        if size > 0:
            size = PCA_SIZE_TEMPLATE.format(size)
        else:
            size = ""

        stretched = nmpy.around(255.0 * (image / nmpy.amax(image))).astype(nmpy.uint8)
        stretched_path = self.folder / f"stretched-{self.anti_cache_counter}.png"
        imsave(stretched_path, stretched)
        self.anti_cache_counter += 1

        self.byte_stream.set_value(stream.decode(encoding="ascii"))
        self.byte_stream_length.set_text(
            BYTE_STREAM_LENGTH_TEMPLATE.format(stream.__len__())
        )
        with self.details_container.clear():
            ui.table(rows=[{DETAILS_LEGEND[_]: str(__) for _, __ in details.items()}])

        with self.pca_container.clear():
            ui.image(stretched_path).classes("w-1/2 m-auto")
        self.pca_name.set_text(name)
        self.pca_size.set_text(size)

    def _UpdateByteStreamLength(self, byte_stream: h.Any, /) -> None:
        """"""
        value = byte_stream.value
        if value is None:
            length = 0
        else:
            length = value.__len__()
        self.byte_stream_length.set_text(BYTE_STREAM_LENGTH_TEMPLATE.format(length))


def Main() -> None:
    """"""
    app = app_t()
    app.Start()


if __name__ in ("__main__", "__mp_main__"):
    #
    Main()
