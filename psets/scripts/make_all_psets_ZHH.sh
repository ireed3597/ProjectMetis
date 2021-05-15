###############
# GenSim pset #
###############

export SCRAM_ARCH=slc6_amd64_gcc630

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_3_18/src ] ; then
  echo release CMSSW_9_3_18 already exists
else
  scram p CMSSW CMSSW_9_3_18
fi
cd CMSSW_9_3_18/src
eval `scram runtime -sh`

# Download fragment from McM
curl -s -k https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_fragment/HIG-RunIIFall17wmLHEGS-05498 --retry 3 --create-dirs -o Configuration/GenProduction/python/HIG-RunIIFall17wmLHEGS-05498-fragment.py
[ -s Configuration/GenProduction/python/HIG-RunIIFall17wmLHEGS-05498-fragment.py ] || exit $?;
scram b -j 20
cd ../..

EVENTS=643

SEED=$(($(date +%s) % 100 + 1))

# cmsDriver command
cmsDriver.py Configuration/GenProduction/python/HIG-RunIIFall17wmLHEGS-05498-fragment.py --python_filename HIG-RunIIFall17wmLHEGS-05498_1_cfg.py --eventcontent RAWSIM,LHE --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM,LHE --fileout file:HIG-RunIIFall17wmLHEGS-05498.root --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${SEED})" --step LHE,GEN,SIM --geometry DB:Extended --era Run2_2017 --no_exec --mc -n $EVENTS --nThreads 1 || exit $? ;

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

EVENTS=544

# cmsDriver command
cmsDriver.py  --python_filename HIG-RunIIFall17DRPremix-07247_1_cfg.py --eventcontent PREMIXRAW --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW --fileout file:HIG-RunIIFall17DRPremix-07247_0.root --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer17PrePremix-MCv2_correctPU_94X_mc2017_realistic_v9-v1/GEN-SIM-DIGI-RAW" --conditions 94X_mc2017_realistic_v11 --step DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:2e34v40 --filein file:HIG-RunIIFall17wmLHEGS-05498.root --datamix PreMix --era Run2_2017 --no_exec --mc -n $EVENTS --nThreads 1 || exit $? ;

cmsDriver.py  --python_filename HIG-RunIIFall17DRPremix-07247_2_cfg.py --eventcontent AODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier AODSIM --fileout file:HIG-RunIIFall17DRPremix-07247.root --conditions 94X_mc2017_realistic_v11 --step RAW2DIGI,RECO,RECOSIM,EI --filein file:HIG-RunIIFall17DRPremix-07247_0.root --era Run2_2017 --runUnscheduled --no_exec --mc -n $EVENTS --nThreads 1 || exit $? ;

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
cmsDriver.py  --python_filename HIG-RunIIFall17MiniAODv2-07295_1_cfg.py --eventcontent MINIAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier MINIAODSIM --fileout file:HIG-RunIIFall17MiniAODv2-07295.root --conditions 94X_mc2017_realistic_v14 --step PAT --scenario pp --filein file:HIG-RunIIFall17DRPremix-07247.root --era Run2_2017,run2_miniAOD_94XFall17 --runUnscheduled --no_exec --mc -n $EVENTS --nThreads 1 || exit $? ;

################
# nanoAOD pset #
################

export SCRAM_ARCH=slc6_amd64_gcc700

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_2_24_patch1/src ] ; then
  echo release CMSSW_10_2_24_patch1 already exists
else
  scram p CMSSW CMSSW_10_2_24_patch1
fi
cd CMSSW_10_2_24_patch1/src
eval `scram runtime -sh`

scram b -j 20
cd ../..

EVENTS=10000

# cmsDriver command
cmsDriver.py  --python_filename HIG-RunIIFall17NanoAODv7-04791_1_cfg.py --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:HIG-RunIIFall17NanoAODv7-04791.root --conditions 102X_mc2017_realistic_v8 --step NANO --filein "dbs:/ZHHTo4B_CV_1_0_C2V_1_0_C3_1_0_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/MINIAODSIM" --era Run2_2017,run2_nanoAOD_94XMiniAODv2 --no_exec --mc -n $EVENTS --nThreads 1 || exit $? ;
