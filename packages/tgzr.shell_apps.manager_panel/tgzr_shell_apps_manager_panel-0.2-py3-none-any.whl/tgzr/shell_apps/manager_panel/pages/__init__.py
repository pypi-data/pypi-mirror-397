from nicegui import ui

from tgzr.nice.tgzr_visid import TGZRVisId
from tgzr.nice import layout
from tgzr.shell.session import get_default_session, set_default_session, Session

from ..components.studios_tab import studios_tab
from ..components.state import State


async def welcome_tab(state: State):
    with ui.row(align_items="center").classes("w-full h-full"):
        with ui.column(align_items="center").classes("w-full text-xl"):
            ui.label("Welcome to TGZR Manager")
            ui.label("Select a section")
            ui.label("⬅️ here")


async def apps_tab(state: State):
    with ui.row(wrap=False).classes("w-full"):
        with ui.column(align_items="center").classes("w-full"):
            ui.label("Apps").classes("text-xl")


async def install_tab(state: State):
    with ui.column(align_items="center").classes("w-full"):
        ui.button("Create new installation", icon="sym_o_location_on")
        ui.button("Duplicate this installation", icon="sym_o_moved_location")
        ui.button(
            "Remove this installation", icon="sym_o_location_off", color="negative"
        )


async def dev_tab(state: State):
    with ui.row(wrap=False).classes("w-full"):
        with ui.column(align_items="center").classes("w-full"):
            ui.label("Dev Tools").classes("text-xl")


def render_session_dialog(state):
    with ui.dialog().props(
        'backdrop-filter="blur(4px) brightness(40%)"'
    ) as session_dialog, ui.card():
        with ui.column(align_items="center").classes("text-md tracking-wide"):
            ui.label("Settings").classes("text-4xl font-thin tracking-[.5em]")
            with ui.column().classes("w-full"):
                verbose_cb = ui.checkbox("Verbose", value=False)
                home_input = ui.input("Home", value="/path/to/session/home")
            with ui.row().classes("w-full"):
                ui.space()
                ui.button(
                    "Apply",
                    on_click=lambda: session_dialog.submit(
                        (verbose_cb.value, home_input.value)
                    ),
                )

    def update_dialog():
        session = state.session
        if session is None:
            verbose_cb.set_value(False)
            home_input.set_value("")
        else:
            verbose_cb.set_value(session.config.verbose)
            home_input.set_value(str(session.home))

    session_dialog.on("show", update_dialog)
    return session_dialog


@ui.page("/", title="TGZR - Manager Panel")
async def main():
    session = get_default_session()

    state = State(session=session)

    visid = TGZRVisId()
    default_tab_name = None  # use welcome
    default_tab_name = "Studios"  # tmp for dev

    tab_renderers = dict(
        studios=studios_tab,
        apps=apps_tab,
        install=install_tab,
        dev=dev_tab,
    )

    async def change_tab(e):
        tab_name = e.value
        await render_tab_content.refresh(tab_name)

    @ui.refreshable
    async def render_tab_content(tab_name: str | None = None):
        renderer = None
        if tab_name is not None:
            renderer = tab_renderers.get(tab_name.lower())
        if renderer is None:
            renderer = welcome_tab

        await renderer(state)

    session_dialog = render_session_dialog(state)

    async def edit_settings():
        result = await session_dialog
        try:
            verbose, home = result
        except TypeError:
            return
        print(verbose, home)

        # s = session
        # if s is None:
        #     s = get_default_session()
        # if s is None:
        s = Session(home)
        s.config.verbose = verbose
        s.set_home(home)
        state.session = s
        # set_default_session(s)

    if session is None:
        await edit_settings()

    with layout.fullpage():
        with ui.row(align_items="center").classes("p-5 w-full"):
            visid.logo(classes="w-16")
            with ui.row(align_items="baseline"):
                ui.label("TGZR").classes("text-5xl font-thin tracking-[1em]")
                ui.label("Manager").classes("text-2xl font-thin tracking-[1em]")
            ui.space()
            ui.button(icon="settings", color="W", on_click=edit_settings).props(
                "flat size=1em"
            )

        with ui.row(wrap=False).classes("w-full h-full"):
            with ui.tabs(on_change=change_tab, value=default_tab_name).classes(
                "xw-full"
            ).props("vertical") as tabs:
                ui.tab("Studios")
                ui.tab("Apps")
                ui.tab("Install")
                ui.tab("Dev")
            with ui.column().classes("w-full h-full p-5"):
                await render_tab_content(default_tab_name)
