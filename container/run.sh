#!/usr/bin/env bash

python /got/analyze.py /subject

python /got/stack_plot.py --outfile=/output/stack_plot.png /got/cohorts.json

CMD="python /got/survival_plot.py"

if [ "$GOT_SURVIVAL_YEARS" ]; then
  CMD="${CMD} --years=${GOT_SURVIVAL_YEARS}"
fi

if [ "$GOT_SURVIVAL_FIT" ]; then
  CMD="${CMD} --exp-fit"
fi

CMD="${CMD} --outfile=/output/survival_plot.png /got/survival.json"
$CMD
