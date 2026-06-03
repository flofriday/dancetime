# dancetime

![screenshot](screenshot.png)

A website to find dance events in Vienna.

[Live Website](https://dancetime.flofriday.dev/)

## Features

A couple of my friends and I love to go (ballroom) dancing in Vienna. However,
looking up a couple websites every week can be quite tedious. So this tool
crawls all of them normalizes them into a uniform format and outputs them as
html, csv, json and as iCalendar to embed in your calendar.

At the moment it downloads from:
- [Ballsaal (Kraml)](https://www.ballsaal.at/termine_tickets/?no_cache=1)
- [Chris](https://www.tanzschulechris.at/perfektionen/tanzcafe_wien_1)
- [Dance4Fun](https://danceforfun.at/termine/)
- [Dorner](https://tanzdorner.at/#perfektion)
- [Immervoll](https://www.tanzschule-immervoll.at/events/)
- [Kopetzky](https://kopetzky.at/Perfektion)
- [Rueff](https://tanzschulerueff.at/)
- [Schwebach](https://schwebach.at/events/) (Tanzcafe only; Perfektionen not listed on events page)
- [Stanek](https://www.tanzschulestanek.at/about-4)
- [Strobl](https://www.tanzschule-strobl.at/perfektion.html)
- [Wagner](https://tanzschule-wagner.at/kurse/mehr.html)
- [Mühlsiegl](https://www.muehlsiegl.at/index.php/tanzschule-wien)
- [Svabek](https://www.svabek.at/perfektionen/)
- [Watzek](https://www.watzek.at/tanzschule/perfektion.php)
- [Dimitar Stefanin](https://dimitarstefanin.com/)

## Build it yourself

You need [uv](https://github.com/astral-sh/uv) (which manages pythons packages
and even installs python itself if no matching version is found on your system)
and [node](https://nodejs.org/en/) with [npm](https://www.npmjs.com/package/npm).

```bash
npm install
npx tailwindcss -i template.css -o index.css
uv run main.py
```

**Note:** While working on the frontend it might be quite handy to add the
`--watch` flag to the tailwind command so that it will automatically rebuild the
css.

## Usage

```
usage: DanceTime [-h] [--output OUTPUT]

Aggregate dance envents and compile them into multiple formats.

options:
  -h, --help       show this help message and exit
  --output OUTPUT  folder into which the outputs should be written.
```

## How we deploy

We directly deploy the main branch to [dancetime.flofriday.dev](https://dancetime.flofriday.dev)
with our CI/CD [GitHub Action](https://docs.github.com/en/actions).

We deploy with docker:
```
docker build -t dancetime .
docker run -p 5000:5000 dancetime
```

The service should now be available at http://localhost:5000
Note that the container needs some time to build the page, but you can cache the output 
between runs by mounting a volume on `/app/dist`.

## Contributing

Contributions are very welcome. At the moment I only ask you to use [ruff](https://docs.astral.sh/ruff/) to
format your code. You are awesome 😊🎉

```bash
ruff format
ruff check --fix
```
