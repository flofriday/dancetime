import dateparser

from event import DanceEvent
from timeutil import Weekday, weekly_event

MUEHLSIEGL_WEBSITE = "https://www.muehlsiegl.at/index.php/tanzschule-wien"
MUEHLSIEGL_DESCRIPTION = (
    "Schönbrunner Straße 249-251, 1120 Wien\n"
    "Perfektionsabend — Standard/Latein im großen Saal, "
    "Boogie/Jive/Rock'n'Roll im kleinen Saal parallel."
)


# https://www.muehlsiegl.at/ — Freitag 20:00–22:00 laut Verzeichnis/Programm
# FIXME: yes this whole approach is a bit hacky and means that if the content
# on the website changes we need to change code. Even worse we probably won't
# notice that the website changes.
def create_perfections() -> list[DanceEvent]:
    return weekly_event(
        Weekday.FRI,
        DanceEvent(
            starts_at=dateparser.parse("20:00"),
            ends_at=dateparser.parse("22:00"),
            name="Perfektion",
            price_euro_cent=None,
            description=MUEHLSIEGL_DESCRIPTION,
            dancing_school="Mühlsiegl",
            website=MUEHLSIEGL_WEBSITE,
        ),
    )


def download_muehlsiegl() -> list[DanceEvent]:
    return create_perfections()
