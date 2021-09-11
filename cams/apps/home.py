"""
웹사이트의 기본 뷰
현재 - 애플리케이션 업데이트 내역을 표시
추후 - 공지사항 등 표시할 예정
"""

# region ---- imports ----

from apps.imports import *

# endregion

debug("loading...")


def loadNotes(fileName) -> list:
    """텍스트 파일의 내용을 행 리스트로 리턴한다"""

    fn = path.join(app.server.root_path, __package__, fileName)
    f = open(fn, "r", encoding="utf-8")
    notes = f.readlines()
    f.close()
    return [n.strip("\r\n") for n in notes]


def layout():
    debug(layout, f"entering...")
    app.title = "B2F - Home"

    notes = [f"{x}\n" for x in loadNotes("update_notes.txt")]
    updating = [f"{x}\n" for x in loadNotes("updating.txt")]

    return html.Div(
        [
            html.H3("Updating..."),
            html.Pre(updating),
            html.Hr(),
            html.H3("Update Notes"),
            html.Pre(notes),
        ],
        className="home-content",
    )


add_page(layout, "Home", 10)
add_page(layout, addPath="/")

# testing
# layout()
