# Hgg-MC-Generation
Tools for generating MC -> CMS nanoAOD.
## Production of ttHH samples

Minimal set of instructions for getting to the submission of private nanoAOD for ttHH analysis

### Step 0: Pull this repo
That is obvious, make sure you are running the latest version of samples

### Step 1: setup [ProjectMetis](https://github.com/aminnj/ProjectMetis) 
Clone and set up ProjectMetis:
```
git clone https://github.com/aminnj/ProjectMetis.git
cd ProjectMetis/
source setup.sh 
cd ..
```
### Step 2: Submit jobs:
You can submit jobs with: 
```
 python submit_jobs.py --tag <pick_a_tag_Name> --config config/config_ttHH_TprimeTprime_UL17_lowMass.json --output_name nanoaod.root --events_total 100000 --events_per_job 400
```
The effects of the options are explained running ```submit_jobs --help ```

For Tprime samples 100000 events per-mass-point per-channel per-year are recommended (submit with ```-events_total 50000```  for 2016, as it will run both pre and post VFP). 
400 events per job results in jobs running for ~4 hours. 
```config_ttHH_TprimeTprime_UL17_lowMass.json``` and ```config_ttHH_TprimeTprime_UL17_lowMass.json```  contain configurations for the 2016 and 2017 mass points that need resubmission.

## Practical example on how to prepare/tweak/test with MC -> nanoAOD workflow
We'll take an existing ttHH, HH->4b CMS sample
```
/TTHHTo4b_5f_LO_TuneCP5_13TeV_madgraph_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM
```

and generate MC -> nanoAOD. We'll also see how to change the physics content of this sample, if desired.

### Step 1: create psets
Go to [DIS2](http://uaf-8.t2.ucsd.edu/~namin/dis2/) and paste the existing sample's name in the Query box, with "chain" selected as the query type.

First, create a valid grid certificate with `voms-proxy-init --voms cms`.
Then, follow the instructions you see on DIS to create an executable.
Here is an example for the ttHH sample:
```
############
# LHE pset #
############

export SCRAM_ARCH=slc6_amd64_gcc630

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_3_9_patch1/src ] ; then
  echo release CMSSW_9_3_9_patch1 already exists
else
  scram p CMSSW CMSSW_9_3_9_patch1
fi
cd CMSSW_9_3_9_patch1/src
eval `scram runtime -sh`

# Download fragment from McM
curl -s -k https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_fragment/HIG-RunIIFall17wmLHEGS-03470 --retry 3 --create-dirs -o Configuration/GenProduction/python/HIG-RunIIFall17wmLHEGS-03470-fragment.py
[ -s Configuration/GenProduction/python/HIG-RunIIFall17wmLHEGS-03470-fragment.py ] || exit $?;
scram b -j 20
cd ../..

EVENTS=393

SEED=$(($(date +%s) % 100 + 1))

# cmsDriver command
cmsDriver.py Configuration/GenProduction/python/HIG-RunIIFall17wmLHEGS-03470-fragment.py --python_filename HIG-RunIIFall17wmLHEGS-03470_1_cfg.py --eventcontent RAWSIM,LHE --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM,LHE --fileout file:HIG-RunIIFall17wmLHEGS-03470.root --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${SEED})" --step LHE,GEN,SIM --geometry DB:Extended --era Run2_2017 --no_exec --mc -n $EVENTS --nThreads 1 || exit $? ;

###############
# Premix pset #
###############

export SCRAM_ARCH=slc6_amd64_gcc630

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_4_7/src ] ; then
  echo release CMSSW_9_4_7 already exists
else
  scram p CMSSW CMSSW_9_4_7
fi
cd CMSSW_9_4_7/src
eval `scram runtime -sh`

scram b -j 20
cd ../..

EVENTS=875

# cmsDriver command
cmsDriver.py  --python_filename HIG-RunIIFall17DRPremix-04017_1_cfg.py --eventcontent PREMIXRAW --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW --fileout file:HIG-RunIIFall17DRPremix-04017_0.root --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer17PrePremix-MCv2_correctPU_94X_mc2017_realistic_v9-v1/GEN-SIM-DIGI-RAW" --conditions 94X_mc2017_realistic_v11 --step DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:2e34v40 --filein file:HIG-RunIIFall17wmLHEGS-03470.root --datamix PreMix --era Run2_2017 --no_exec --mc -n $EVENTS --nThreads 1 || exit $? ;

# cmsDriver command
cmsDriver.py  --python_filename HIG-RunIIFall17DRPremix-04017_2_cfg.py --eventcontent AODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier AODSIM --fileout file:HIG-RunIIFall17DRPremix-04017.root --conditions 94X_mc2017_realistic_v11 --step RAW2DIGI,RECO,RECOSIM,EI --filein file:HIG-RunIIFall17DRPremix-04017_0.root --era Run2_2017 --runUnscheduled --no_exec --mc -n $EVENTS --nThreads 1 || exit $? ;

################
# miniAOD pset #
################

export SCRAM_ARCH=slc6_amd64_gcc630

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_4_7/src ] ; then
  echo release CMSSW_9_4_7 already exists
else
  scram p CMSSW CMSSW_9_4_7
fi
cd CMSSW_9_4_7/src
eval `scram runtime -sh`

scram b -j 20
cd ../..

EVENTS=4800

# cmsDriver command
cmsDriver.py  --python_filename HIG-RunIIFall17MiniAODv2-03949_1_cfg.py --eventcontent MINIAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier MINIAODSIM --fileout file:HIG-RunIIFall17MiniAODv2-03949.root --conditions 94X_mc2017_realistic_v14 --step PAT --scenario pp --filein "dbs:/TTHHTo4b_5f_LO_TuneCP5_13TeV_madgraph_pythia8/RunIIFall17DRPremix-PU2017_94X_mc2017_realistic_v11-v1/AODSIM" --era Run2_2017,run2_miniAOD_94XFall17 --runUnscheduled --no_exec --mc -n $EVENTS --nThreads 1 || exit $? ;

################
# nanoAOD pset #
################

export SCRAM_ARCH=slc6_amd64_gcc700

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_2_22/src ] ; then
  echo release CMSSW_10_2_22 already exists
else
  scram p CMSSW CMSSW_10_2_22
fi
cd CMSSW_10_2_22/src
eval `scram runtime -sh`

scram b -j 20
cd ../..

EVENTS=10000

# NOTE: make sure to replace "NANOEDMOADSIM" with "NANOADOSIM" everywhere you see it in the cmsDriver command. Otherwise, you will not be able to read your nanoAODs properly
# cmsDriver command
cmsDriver.py  --python_filename HIG-RunIIFall17NanoAODv7-02462_1_cfg.py --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:HIG-RunIIFall17NanoAODv7-02462.root --conditions 102X_mc2017_realistic_v8 --step NANO --filein "dbs:/TTHHTo4b_5f_LO_TuneCP5_13TeV_madgraph_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM" --era Run2_2017,run2_nanoAOD_94XMiniAODv2 --no_exec --mc -n $EVENTS --nThreads 1 || exit $? ;
```
### Step 2: modify GenSim pset physics content (if desired)
This MC sample generates ttHH, HH->4b events, but let's say we want to instead generate ttHH, HH->bbgg events.
To do this, we need to modify the GenSim pset, `HIG-RunIIFall17wmLHEGS-03470_1_cfg.py`.

In the pset, we see:
```
processParameters = cms.vstring('25:m0 = 125.0',
    '25:onMode = off',
    '25:onIfMatch = 5 -5'),
```

The PDG ID of the Higgs is 25, and the PDG of the b quark is 5, so this is saying that we set mH = 125, and require it decay into b quarks.

We want to modify this so one H decays into b quarks, while the other H decays into photons:
```
processParameters = cms.vstring('25:m0 = 125.0',
    '25:onMode = off',
    '25:onIfMatch = 5 -5',
    '25:onIfMatch = 22 22', # allow H->gg decays
    'ResonanceDecayFilter:filter = on', # turn on a resonance decay filter so we can specify HH->ggbb
    'ResonanceDecayFilter:exclusive = on', #off: require at least the specified number of daughters, on: require exactly the specified number of daughters (we want on)
    'ResonanceDecayFilter:mothers = 25', # apply this filter only to the Higgs's
    'ResonanceDecayFilter:daughters = 5,5,22,22' # require HH->bbgg
)
```

### Step 3: modify pset input/output filenames
For metis to find the correct files when running the jobs, it's easier if the input/output names of each step are done in a consistent way.

In the LHE/GenSim pset, set the output names as:
```
process.RAWSIMoutput = cms.OutputModule("PoolOutputModule",
   ...
   fileName = cms.untracked.string('file:GENSIM.root'), # you change this line
...
process.LHEoutput = cms.OutputModule("PoolOutputModule",
   ...
   fileName = cms.untracked.string('file:GENSIM_inLHE.root'), # you change this line
```

In the Premix pset, replace the `process.source` lines with:
```
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('file:GENSIM.root'),
    secondaryFileNames = cms.untracked.vstring()
)
```
and change the output file:
```
process.PREMIXRAWoutput = cms.OutputModule("PoolOutputModule",
   ...
   fileName = cms.untracked.string('file:step1.root'), # you change this line
``` 

Do the same for the rest of the psets (AOD, miniAOD, nanoAOD). You can name them whatever they like, but make sure they match they are consistent so one step will correctly grab the output of the previous step.

Finally, make sure that the output of the nanoAOD pset matches what metis expects for the final output file name.
If you have not changed the executable template, this should probably be `output.root`, e.g.
```
process.NANOAODSIMoutput = cms.OutputModule("NanoAODOutputModule",
    ...
    fileName = cms.untracked.string('file:output.root'),
``` 

### Step 4: submit jobs with [ProjectMetis](https://github.com/aminnj/ProjectMetis) 
First, clone and set up ProjectMetis:
```
git clone https://github.com/aminnj/ProjectMetis.git
cd ProjectMetis/
source setup.sh 
cd ..
```


