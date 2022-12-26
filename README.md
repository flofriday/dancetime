# dancetime 

A website generator to aggregate dance events in Vienna.

## Features 

A couple of my friends and I love to go (ballroom) dancing in Vienna. However, 
looking up a couple websites every week can be quite tedious. So this tool
crawls all of them normalizes them into a uniform format and outputs them as 
csv (and html and json in the future.)

At the moment it downloads from:
- [ballsaal.at](https://www.ballsaal.at/termine_tickets/?no_cache=1)

## Build it yourself

You need python3 with pip and venv, and node with npm.

```bash
npm install
npx tailwindcss -i ./src/input.css -o ./dist/output.css
python3 -m venv venv
source venv/bin/activate
pyhton -m pip install -r requirements.txt
python main.py
```

**Note: ** While working on the frontend it might be quite handy to add the
`--watch` flag to the tailwind command so that it will automatically rebuild the 
css.

## How we deploy

At the moment I haven't deployed it yet but I plan on simply running a cron job
every day that downloads the events and renders them into a static html file
which I will host on my server with nginx.

## Contributing

Contributions are very welcome. At the moment I only ask you to use black to 
format your code.