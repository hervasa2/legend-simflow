(production)=

# Production

Run a production by using one of the provided site-specific profiles
(recommended):

```console
> snakemake --workflow-profile workflow/profiles/<profile-name>
```

If no system-specific profiles are provided, the `--workflow-profile` option can
be omitted. Snakemake will use the `default` profile.

```console
> snakemake
```

The `--config` command line option is very useful to override configuration
values. It can be used, for example, to restrict the production to a subset of
simulations (a "simlist"):

```console
> snakemake --config simlist="mylist.txt" [...]
```

where `mylist.txt` is a text file in the format:

```
stp.fibers_Ra224_to_Pb208
hit.hpge_bulk_2vbb
...
```

One can even just directly pass a comma-separated list:

```console
> snakemake --config simlist="stp.fibers_Ra224_to_Pb208,hit.hpge_bulk_2vbb
```

Remember that Snakemake accepts individual output file paths as arguments. If
supplied, Snakemake will only produce those.

```console
> snakemake /../generated/tier/stp/sis1_z8640_slot3_Pb214_to_Po214/l200p15-sis1_z8640_slot3_Pb214_to_Po214-job_0000-tier_stp.lh5
```

Once the production is over, the `print_stats` rule can be used to display a
table with runtime statistics:

```console
> snakemake -q all print_stats
                                                    wall time [s]         wall time [s]
simid                                                (cumulative)   jobs      (per job)  primaries
-----                                               -------------   ----  -------------  ---------
hit.fibers_Ra224_to_Pb208                                83:20:00    100        0:50:00   1.00E+08
stp.fibers_Ra224_to_Pb208                                58:20:35    100        0:35:00   1.00E+08
stp.fibers_Rn222_to_Po214                                33:20:00    100        0:20:00   1.00E+08
...                                                            ...    ...            ...        ...
```

Find some useful Snakemake command-line options at the bottom of this page.

## Selective step execution with `make_steps`

The `make_steps` configuration option controls which workflow steps are loaded
into the Snakemake DAG. Only the rule files for the listed steps are included,
so outputs of excluded steps are treated as pre-existing source files rather
than targets — Snakemake will neither build nor invalidate them.

**Running a single step in isolation** is the most common use case. For example,
to rebuild only the `hit` tier outputs while leaving `stp` files untouched:

```yaml
make_steps:
  - hit
```

or equivalently at the command line:

```console
> snakemake --config make_steps="[hit]"
```

**Running contiguous steps** works the same way — just list all the steps you
need. To run the full parameter and post-processing chain without re-running the
remage simulations:

```yaml
make_steps:
  - par
  - opt
  - hit
  - evt
  - cvt
```

:::{warning}

The `par` step builds the parameters consumed by both `opt` and `hit` (HPGe
drift-time maps, current-pulse models, energy-resolution and A/E models, and
run-statistics partitioning files). If `opt` or `hit` is included in
`make_steps` without `par`, those parameter files **must already exist on
disk**. Omitting `par` is only safe when the parameters have been produced in a
previous run and have not changed.

:::

:::{note}

`vtx` and `par` cannot be used as step prefixes in `simlist` items (e.g.
`par.myid` is invalid) because neither step produces simid-scoped output files.

:::

## Benchmarking runs

This workflow implements the possibility to run special "benchmarking" runs in
order to evaluate the speed of simulations, for tuning the number of events to
simulate for each simulation run.

1. Create a new, dedicated production cycle (see above)
2. Enable benchmarking in the configuration file and customize further settings
3. Start the production as usual.

Snakemake will spawn a single job (with the number of primary events specified
in the configuration file) for each simulation. Once the production is over, the
results can be summarized via the `print_benchmark_stats` rule:

```console
> snakemake print_benchmark_stats
simid                                runtime [sec]  speed (hot loop) [ev/sec]  evts / 1h  jobs (1h) / 10^8 evts
-----                                -------------  -------------------------  ---------  ---------------------
stp.sis1_z8430_slot2_Bi212_to_Pb208          139.0                     717.70    2583720                     38
stp.sis1_z8580_slot2_Pb214_to_Po214          167.0                     596.99    2149164                     46
stp.sis1_z8630_slot2_Bi212_to_Pb208          135.0                     740.46    2665656                     37
...                                            ...                        ...        ...                    ...
```

Which computes statistics by inspecting the `stp`-tier (_remage_) logs.

:::{note}

The benchmarking statistics refer exclusively to the hot Geant4 simulation loop.
Overheads such as application initialization or remage built-in post processing
are not taken into account.

:::
