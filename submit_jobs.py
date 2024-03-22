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
import re

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--tag", help = "tag to identify this set of MC", type=str)
parser.add_argument("--output_name" , help= "name of the final output file", type=str, default= "nanoaod.root")
parser.add_argument("--output_directory" , help= "path on ceph to write to", type=str, default= "/ceph/cms/store/user/azecchin")
parser.add_argument("--config", help = "path to json file containing list of samples and their psets", type=str, default = "config/config_all.json")
parser.add_argument("--events_total", help = "number of events to produce (per sample)", type=int, default = 1000)
parser.add_argument("--events_per_job", help = "number of generated events per job", type=int, default = 200)
parser.add_argument("--samples", help = "which samples to generate MC for (will produce for all samples in config file if not specified", type=str, default = "")
parser.add_argument("--remake_tar", help = "remake tar file (will be made either way if the tar file doesn't already exist)", action = "store_true")
parser.add_argument("--run_local", help = "run using local input files", action = "store_true")
parser.add_argument("--azure", help = "run on Azure computing cloud", action = "store_true")
args = parser.parse_args()

# intermediate steps local output

local_sets=[
    ("ttH2_HHToBBGG_2HDMtII_mH300_LO_2018", "/ceph/cms/store/user/azecchin/ttH2_HHToBBGG_2HDMtII_mH300_LO_2018_MINI_testIII"),
    # ("ttHH_HHToBBGG_5f_LO_2017", "/ceph/cms/store/user/azecchin/nanoAOD_runII/ttHH_HHToBBGG_5f_LO_2017_MINI_16022022"),
    # ("ttHH_HHToBBGG_5f_LO_2018", "/ceph/cms/store/user/azecchin/nanoAOD_runII/ttHH_HHToBBGG_5f_LO_2018_MINI_10022022_v2"),
    # ("ttHH_HHToTAUTAUGG_5f_LO_2017", "/ceph/cms/store/user/azecchin/nanoAOD_runII/ttHH_HHToTAUTAUGG_5f_LO_2017_MINI_16022022"),
    # ("ttHH_HHToTAUTAUGG_5f_LO_2018", "/ceph/cms/store/user/azecchin/nanoAOD_runII/ttHH_HHToTAUTAUGG_5f_LO_2018_MINI_11022022"),
    # ("ttHH_HHToWWGG_5f_LO_2017", "/ceph/cms/store/user/azecchin/nanoAOD_runII/ttHH_HHToWWGG_5f_LO_2017_MINI_16022022"),
    # ("ttHH_HHToWWGG_5f_LO_2018", "/ceph/cms/store/user/azecchin/nanoAOD_runII/ttHH_HHToWWGG_5f_LO_2018_MINI_11022022"),
]


# gridpacks locations for privately produced packs
from gridpacks import gridpacks

# custom nano setup
nano_cmssw_ver = "CMSSW_10_6_26"

CONDOR_SUBMIT_PARAMS = {
        "classads" : [
            ["param_nevents", args.events_per_job],
            ["metis_extraargs", ""],
            # ["JobBatchName",  "HggMCProduction_" + args.tag],
            # ["SingularityImage","/cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel6-m202006"] 
            # ["SingularityImage","/cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel7-m202006"] # we want slc7
            ["RequestK8SNamespace", "cms-ucsd-t2"],  #Franny setup
            ["SingularityImage", "/cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel7-m202006"]
        ],
        "requirements_line": 'Requirements = (HAS_SINGULARITY=?=True) && (TARGET.K8SNamespace =!= "abc")'
}

if args.azure:
    CONDOR_SUBMIT_PARAMS["classads"] += [["memory",  1950]]
    CONDOR_SUBMIT_PARAMS["classads"] += [["cpus", 1]]
    CONDOR_SUBMIT_PARAMS["classads"] += [["IS_CLOUD_JOB", "yes"]]
    CONDOR_SUBMIT_PARAMS["sites"] = "T2_US_UCSD"

else:
    CONDOR_SUBMIT_PARAMS["sites"] = "T2_US_UCSD" # Disabling other T2 for using local gripacks ("T2_US_CALTECH,T2_US_MIT,T2_US_WISCONSIN,T2_US_Nebraska,T2_US_Purdue,T2_US_Florida")


with open(args.config, "r") as f_in:
    samples_config = json.load(f_in)

samples = samples_config.keys()

if args.samples != "" and args.samples != "all":
    if "," in args.samples: # not so elegant way to split csv lists and regex 
        samples = args.samples.split(",")
    else:
        arg_smpls = re.compile(args.samples)
        samples = filter(arg_smpls.match,samples)

TEMPLATE = "executables/template.sh"
def create_executable(tag, sample, config_info):
    executable = "executables/condor_exe_%s_%s.sh" % (sample, tag)
    with open(TEMPLATE, "r") as f_in:
        lines = f_in.readlines()

    with open(executable, "w") as f_out:
        for line in lines:
            #STEPS: "gen", "step1", "step2", "step3", "step4", "mini", "nano"
            for step in ["gen", "step1", "step2", "step3", "step4", "mini", "nano"]: 
                for item in ["CFG", "CMSSW", "SCRAM_ARCH"]:
                    name = "%s_%s_TEMP" % (step, item)
                    if name in line:
                        result = config_info[step][item]
                        if item == "CFG":
                            result = "psets/UL/" + result
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
            files.append("psets/UL/" + step_info["CFG"])
            #files += "psets/" + step_info["CFG"] + " "

    files = list(set(files))
    files = " ".join(files)
    #files = files.join(" ")

    print("Making tarfile with the following files:")
    for file in files.split():
        print("\t %s" % file)
    if nano_cmssw_ver:
        print("\t Custom nano CMSSW version: %s"%nano_cmssw_ver)
    os.system("XZ_OPT='-3e -T24' tar -Jc --exclude='.git' --exclude='*.root' --exclude='*.tar*' --exclude='*.out' --exclude='*.err' --exclude='*.log' --exclude '*.nfs*' %s -f %s %s" % (files, tarfile, nano_cmssw_ver))
    return tarfile

def submit_jobs(output_directory, tag, samples, events_total, events_per_output, tarfile):
    # Long loop to monitor jobs and resubmit failed jobs
    for i in range(10000):
        total_summary = {}

        # Loop through samples
        for sample in samples:
            print ("Working on sample {}".format(sample))
            if args.run_local: continue
            config_info = samples_config[sample]

            executable = create_executable(tag, sample, config_info)

            if sample in gridpacks.keys():
                gridpack = gridpacks[sample]
            else: gridpack = ""
            print ("sample {} has this gridpack {}".format(sample,gridpack))
            task = CondorTask(
                    sample = DummySample(
                        N = int(float(events_total) / float(events_per_output)),
                        nevents = events_total,
                        dataset = "/" + sample + "_NANOv9"
                    ),
                    tag = tag,
                    special_dir = output_directory,
                    output_name = args.output_name,
                    events_per_output = events_per_output,
                    total_nevents = events_total,
                    split_within_files = True,
                    executable = executable, 
                    open_dataset = False,
                    tarfile = tarfile,
                    additional_input_files = [gridpack],
                    condor_submit_params = CONDOR_SUBMIT_PARAMS
            )

            task.process()
            total_summary[task.get_sample().get_datasetname()] = task.get_task_summary()

        if args.run_local:
            
            config_info = samples_config[sample]

            executable = create_executable(tag, sample, config_info)

            for sample, loc in local_sets[:]:
                sample = DirectorySample(dataset = "/" + sample + "_NANOv9", location = loc)
                files = [f.name for f in sample.get_files()]
                print ("For sample {} in directory {}, there are {} files".format( sample, loc, len(files)))
                
                task = CondorTask(
                    sample = sample,
                    tag = tag,
                    special_dir = output_directory,
                    output_name = args.output_name,
                    events_per_output = events_per_output,
                    total_nevents = events_total,
                    split_within_files = True,
                    executable = executable, 
                    open_dataset = True,
                    tarfile = tarfile,
                    condor_submit_params = CONDOR_SUBMIT_PARAMS
                )

                task.process()
                total_summary[task.get_sample().get_datasetname()] = task.get_task_summary()

        StatsParser(
                data = total_summary,
                webdir = "~/public_html/dump/Hgg-MC-Production/"
        ).do()

        time.sleep(900) # power nap

tarfile = create_tarfile(
        tag = args.tag,
        samples = samples,
        samples_config = samples_config,
        remake = args.remake_tar 
)

submit_jobs("nanoAOD_runII", args.tag, samples, args.events_total, args.events_per_job, tarfile)
