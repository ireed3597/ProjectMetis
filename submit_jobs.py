"""
Configurable job submission script for generating MC -> nanoAOD.
Inspired by scripts from:
    - Nick Amin: https://github.com/aminnj/scouting/blob/master/generation/submit_jobs.py
    - Daniel Spitzbart: https://github.com/danbarto/tW_scattering/blob/master/production/make_full.py
"""

from metis.CMSSWTask import CMSSWTask
from metis.CondorTask import CondorTask
from metis.Sample import DirectorySample,DummySample
from metis.Path import Path
from metis.StatsParser import StatsParser

import time
import os
import json

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--tag", help = "tag to identify this set of MC", type=str)
parser.add_argument("--config", help = "path to json file containing list of samples and their psets", type=str, default = "config/config_all.json")
parser.add_argument("--events_total", help = "number of events to produce (per sample)", type=int, default = 1000)
parser.add_argument("--events_per_job", help = "number of generated events per job", type=int, default = 200)
parser.add_argument("--samples", help = "which samples to generate MC for (will produce for all samples in config file if not specified", type=str, default = "")
parser.add_argument("--remake_tar", help = "remake tar file (will be made either way if the tar file doesn't already exist)", action = "store_true")
parser.add_argument("--azure", help = "run on Azure computing cloud", action = "store_true")
args = parser.parse_args()


CONDOR_SUBMIT_PARAMS = {
        "classads" : [
            ["param_nevents", args.events_per_job],
            ["metis_extraargs", ""],
            #["JobBatchName",  "HggMCProduction_" + args.tag],
            ["SingularityImage","/cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel6-m202006"]
        ],
        "requirements_line": 'Requirements = (HAS_SINGULARITY=?=True)'
}

if args.azure:
    CONDOR_SUBMIT_PARAMS["classads"] += [["memory",  1950]]
    CONDOR_SUBMIT_PARAMS["classads"] += [["cpus", 1]]
    CONDOR_SUBMIT_PARAMS["classads"] += [["IS_CLOUD_JOB", "yes"]]
    CONDOR_SUBMIT_PARAMS["sites"] = "T2_US_UCSD"

else:
    CONDOR_SUBMIT_PARAMS["sites"] = "T2_US_UCSD,T2_US_CALTECH,T2_US_MIT,T2_US_WISCONSIN,T2_US_Nebraska,T2_US_Purdue,T2_US_Florida"


with open(args.config, "r") as f_in:
    samples_config = json.load(f_in)

if args.samples == "" or args.samples == "all":
    samples = samples_config.keys()
else:
    samples = args.samples.split(",")

TEMPLATE = "executables/template.sh"
def create_executable(tag, sample, config_info):
    executable = "executables/condor_exe_%s_%s.sh" % (sample, tag)
    with open(TEMPLATE, "r") as f_in:
        lines = f_in.readlines()

    with open(executable, "w") as f_out:
        for line in lines:
            for step in ["gen", "step1", "step2", "mini", "nano"]:
                for item in ["CFG", "CMSSW", "SCRAM_ARCH"]:
                    name = "%s_%s_TEMP" % (step, item)
                    if name in line:
                        result = config_info[step][item]
                        if item == "CFG":
                            result = "psets/" + result
                        line = line.replace(name, result)
            f_out.write(line)

    return executable

def create_tarfile(tag, samples, samples_config, remake = False):
    tarfile = "package_%s.tar.gz" % tag
    if os.path.exists(tarfile) and not remake:
        print("Tarfile already exists. Not remaking it.")
        return tarfile
    files = []
    for sample in samples: 
        for step, step_info in samples_config[sample].items(): 
            files.append("psets/" + step_info["CFG"])
            #files += "psets/" + step_info["CFG"] + " "

    files = list(set(files))
    files = " ".join(files)
    #files = files.join(" ")

    print("Making tarfile with the following files:")
    for file in files.split():
        print("\t %s" % file)
    os.system("XZ_OPT='-3e -T12' tar -Jc %s -f %s" % (files, tarfile))
    return tarfile

def submit_jobs(output_directory, tag, samples, events_total, events_per_output, tarfile):
    # Long loop to monitor jobs and resubmit failed jobs
    for i in range(10000):
        total_summary = {}

        # Loop through samples
        for sample in samples:
            config_info = samples_config[sample]

            executable = create_executable(tag, sample, config_info)

            task = CondorTask(
                    sample = DummySample(
                        N = int(float(events_total) / float(events_per_output)),
                        nevents = events_total,
                        dataset = "/" + sample + "_NANO"
                    ),
                    tag = tag,
                    special_dir = output_directory,
                    events_per_output = events_per_output,
                    total_nevents = events_total,
                    split_within_files = True,
                    executable = executable, 
                    open_dataset = False,
                    tarfile = tarfile,
                    condor_submit_params = CONDOR_SUBMIT_PARAMS
            )

            task.process()
            total_summary[task.get_sample().get_datasetname()] = task.get_task_summary()

        StatsParser(
                data = total_summary,
                webdir = "~/public_html/dump/Hgg-MC-Production/"
        ).do()

        time.sleep(300) # power nap

tarfile = create_tarfile(
        tag = args.tag,
        samples = samples,
        samples_config = samples_config,
        remake = args.remake_tar 
)

submit_jobs("nanoAOD_runII", args.tag, samples, args.events_total, args.events_per_job, tarfile)
