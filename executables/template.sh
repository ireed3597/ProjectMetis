#!/bin/bash

OUTPUTDIR=$1
OUTPUTNAME=$2
INPUTFILENAMES=$3
IFILE=$4
PSET=$5
CMSSWVERSION=$6
SCRAMARCH=$7
NEVTS=$8
FIRSTEVT=$9
EXPECTEDNEVTS=${10}
OTHEROUTPUTS=${11}
PSETARGS="${@:12}" # since args can have spaces, we take 10th-->last argument as one

# Psets and CMSSW/scram_arch
gencfg="gen_CFG_TEMP"
gen_cmssw="gen_CMSSW_TEMP"
gen_scram_arch="gen_SCRAM_ARCH_TEMP"

step1cfg="step1_CFG_TEMP"
step1_cmssw="step1_CMSSW_TEMP"
step1_scram_arch="step1_SCRAM_ARCH_TEMP"

step2cfg="step2_CFG_TEMP"
step2_cmssw="step2_CMSSW_TEMP"
step2_scram_arch="step2_SCRAM_ARCH_TEMP"

step3cfg="step3_CFG_TEMP"
step3_cmssw="step3_CMSSW_TEMP"
step3_scram_arch="step3_SCRAM_ARCH_TEMP"

step4cfg="step4_CFG_TEMP"
step4_cmssw="step4_CMSSW_TEMP"
step4_scram_arch="step4_SCRAM_ARCH_TEMP"

minicfg="mini_CFG_TEMP"
mini_cmssw="mini_CMSSW_TEMP"
mini_scram_arch="mini_SCRAM_ARCH_TEMP"

nanocfg="nano_CFG_TEMP"
nano_cmssw="nano_CMSSW_TEMP"
nano_scram_arch="nano_SCRAM_ARCH_TEMP"

# Make sure OUTPUTNAME doesn't have .root since we add it manually
OUTPUTNAME=$(echo $OUTPUTNAME | sed 's/\.root//')

export SCRAM_ARCH=${SCRAMARCH}

function getjobad {
    grep -i "^$1" "$_CONDOR_JOB_AD" | cut -d= -f2- | xargs echo
}
function setup_chirp {
    if [ -e ./condor_chirp ]; then
    # Note, in the home directory
        mkdir chirpdir
        mv condor_chirp chirpdir/
        export PATH="$PATH:$(pwd)/chirpdir"
        echo "[chirp] Found and put condor_chirp into $(pwd)/chirpdir"
    elif [ -e /usr/libexec/condor/condor_chirp ]; then
        export PATH="$PATH:/usr/libexec/condor"
        echo "[chirp] Found condor_chirp in /usr/libexec/condor"
    else
        echo "[chirp] No condor_chirp :("
    fi
}
function chirp {
    # Note, $1 (the classad name) must start with Chirp
    condor_chirp set_job_attr_delayed $1 $2
    ret=$?
    echo "[chirp] Chirped $1 => $2 with exit code $ret"
}
function edit_pset {
    NEVTS=$1
    echo "process.maxEvents.input = cms.untracked.int32(${NEVTS})" >> pset.py
    echo "if hasattr(process,'externalLHEProducer'):" >> pset.py
    echo "    process.externalLHEProducer.nEvents = cms.untracked.uint32(${NEVTS})" >> pset.py
    echo "set_output_name(\"${OUTPUTNAME}.root\")" >> pset.py
    if [[ "$INPUTFILENAMES" != "dummy"* ]]; then
        echo "process.source.fileNames = cms.untracked.vstring([" >> pset.py
        for INPUTFILENAME in $(echo "$INPUTFILENAMES" | sed -n 1'p' | tr ',' '\n'); do
            INPUTFILENAME=$(echo $INPUTFILENAME | sed 's|^/ceph/cms||')
            # INPUTFILENAME="root://xrootd.unl.edu/${INPUTFILENAME}"
            echo "\"${INPUTFILENAME}\"," >> pset.py
        done
        echo "])" >> pset.py
    fi
    if [ "$FIRSTEVT" -ge 0 ]; then
        # events to skip, event number to assign to first event
        echo "try:" >> pset.py
        echo "    if not 'Empty' in str(process.source): process.source.skipEvents = cms.untracked.uint32(max(${FIRSTEVT}-1,0))" >> pset.py
        echo "except: pass" >> pset.py
        echo "try:" >> pset.py
        echo "    process.source.firstEvent = cms.untracked.uint32(${FIRSTEVT})" >> pset.py
        echo "except: pass" >> pset.py
    fi
}

function edit_psets {
    seed=$1
    nevents=$2

    # gensim
    #echo "process.externalLHEProducer.args = [\"$gridpack\"]" >> $gencfg
    echo "process.RandomNumberGeneratorService.externalLHEProducer.initialSeed = $seed" >> $gencfg #MG5 GEN
    echo "process.externalLHEProducer.nEvents = $nevents" >> $gencfg #MG5 GEN
    # echo "from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper"  >> $gencfg #SHERPA GEN
    # echo "randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService)"  >> $gencfg #SHERPA GEN
    # echo "randSvc.populate()" >> $gencfg #SHERPA GEN
    echo "process.maxEvents.input = $nevents" >> $gencfg
    echo "process.source.firstLuminosityBlock = cms.untracked.uint32($seed)" >> $gencfg

    #echo "set_output_name(\"output_GEN.root\")" >> $gencfg

    # step1
    echo "process.maxEvents.input = -1" >> $step1cfg
    #echo "process.source.fileNames = cms.untracked.vstring([\"output_GEN.root\"])" >> $step1cfg
    #echo "set_output_name(\"output_STEP1.root\")" >> $step1cfg

    # step2
    echo "process.maxEvents.input = -1" >> $step2cfg
    #echo "process.source.fileNames = cms.untracked.vstring([\"output_STEP1.root\"])" >> $step2cfg
    #echo "set_output_name(\"output_STEP2.root\")" >> $step2cfg

    # step3
    echo "process.maxEvents.input = -1" >> $step3cfg
    #echo "process.source.fileNames = cms.untracked.vstring([\"output_STEP1.root\"])" >> $step3cfg
    #echo "set_output_name(\"output_STEP2.root\")" >> $step3cfg

    # step4
    echo "process.maxEvents.input = -1" >> $step4cfg
    #echo "process.source.fileNames = cms.untracked.vstring([\"output_STEP1.root\"])" >> $step4cfg
    #echo "set_output_name(\"output_STEP2.root\")" >> $step4cfg

    # mini
    echo "process.maxEvents.input = -1" >> $minicfg
    # echo "process.source.fileNames = cms.untracked.vstring([\"output_STEP2.root\"])" >> $minicfg
    # echo "process.MINIAODSIMoutput.fileName=\"miniaod.root\"" >> $minicfg

    # nano
    echo "process.maxEvents.input = -1" >> $nanocfg
    # #echo "process.source.fileNames = cms.untracked.vstring([\"output_MINI.root\"])" >> $nanocfg
    # echo "set_output_name(\"output.root\")" >> $nanocfg

}

function stageout {
    COPY_SRC=$1
    COPY_DEST=$2
    retries=0
    COPY_STATUS=1
    until [ $retries -ge 3 ]
    do
        echo "Stageout attempt $((retries+1)): env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-copy -p -f -t 7200 --verbose --checksum ADLER32 ${COPY_SRC} ${COPY_DEST}"
        env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-copy -p -f -t 7200 --verbose --checksum ADLER32 ${COPY_SRC} ${COPY_DEST}
        COPY_STATUS=$?
        if [ $COPY_STATUS -ne 0 ]; then
            echo "Failed stageout attempt $((retries+1))"
        else
            echo "Successful stageout with $retries retries"
            break
        fi
        retries=$[$retries+1]
        echo "Sleeping for 30m"
        sleep 30m
    done
    if [ $COPY_STATUS -ne 0 ]; then
        echo "Removing output file because gfal-copy crashed with code $COPY_STATUS"
        env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-rm --verbose ${COPY_DEST}
        REMOVE_STATUS=$?
        if [ $REMOVE_STATUS -ne 0 ]; then
            echo "Uhh, gfal-copy crashed and then the gfal-rm also crashed with code $REMOVE_STATUS"
            echo "You probably have a corrupt file sitting on ceph now."
            exit 1
        fi
    fi
}

setup_chirp

echo -e "\n--- begin header output ---\n" #                     <----- section division
echo "OUTPUTDIR: $OUTPUTDIR"
echo "OUTPUTNAME: $OUTPUTNAME"
echo "INPUTFILENAMES: $INPUTFILENAMES"
echo "IFILE: $IFILE"
echo "PSET: $PSET"
echo "CMSSWVERSION: $CMSSWVERSION"
echo "SCRAMARCH: $SCRAMARCH"
echo "NEVTS: $NEVTS"
echo "EXPECTEDNEVTS: $EXPECTEDNEVTS"
echo "OTHEROUTPUTS: $OTHEROUTPUTS"
echo "PSETARGS: $PSETARGS"
# echo  CLASSAD: $(cat "$_CONDOR_JOB_AD")

echo "GLIDEIN_CMSSite: $GLIDEIN_CMSSite"
echo "hostname: $(hostname)"
echo "uname -a: $(uname -a)"
echo "time: $(date +%s)"
echo "args: $@"
echo "tag: $(getjobad tag)"
echo "taskname: $(getjobad taskname)"

echo -e "\n--- end header output ---\n" #                       <----- section division

NEVENTS=$(getjobad param_nevents)

if [ -r "$OSGVO_CMSSW_Path"/cmsset_default.sh ]; then
    echo "sourcing environment: source $OSGVO_CMSSW_Path/cmsset_default.sh"
    source "$OSGVO_CMSSW_Path"/cmsset_default.sh
elif [ -r "$OSG_APP"/cmssoft/cms/cmsset_default.sh ]; then
    echo "sourcing environment: source $OSG_APP/cmssoft/cms/cmsset_default.sh"
    source "$OSG_APP"/cmssoft/cms/cmsset_default.sh
elif [ -r /cvmfs/cms.cern.ch/cmsset_default.sh ]; then
    echo "sourcing environment: source /cvmfs/cms.cern.ch/cmsset_default.sh"
    source /cvmfs/cms.cern.ch/cmsset_default.sh
else
    echo "ERROR! Couldn't find $OSGVO_CMSSW_Path/cmsset_default.sh or /cvmfs/cms.cern.ch/cmsset_default.sh or $OSG_APP/cmssoft/cms/cmsset_default.sh"
    exit 1
fi

function setup_cmssw {
  CMSSW=$1
  export SCRAM_ARCH=$2
  scram p CMSSW $CMSSW
  cd $CMSSW
  eval `scramv1 runtime -sh`
  scramv1 b ProjectRename
  scram b -j3
  eval `scramv1 runtime -sh`
  cd -
}

# Untar psets
mkdir temp
cd temp
cp ../*.gz .
tar xf *.gz

echo "before running: ls -lrth"
ls -lrth

echo -e "\n--- begin running ---\n" #                           <----- section division

chirp ChirpMetisExpectedNevents $EXPECTEDNEVTS

echo "Editing psets with parameters:"
echo $IFILE
echo $NEVENTS
edit_psets $IFILE $NEVENTS

echo "Running the following configs:"
echo $gencfg
echo $step1cfg
echo $step2cfg
echo $step3cfg
echo $step4cfg
echo $minicfg
echo $nanocfg

chirp ChirpMetisStatus "before_cmsRun"


setup_cmssw $gen_cmssw $gen_scram_arch
cmsRun $gencfg

setup_cmssw $step1_cmssw $step1_scram_arch
cmsRun $step1cfg

setup_cmssw $step2_cmssw $step2_scram_arch
cmsRun $step2cfg

setup_cmssw $step3_cmssw $step3_scram_arch
cmsRun $step3cfg

setup_cmssw $step4_cmssw $step4_scram_arch
cmsRun $step4cfg

setup_cmssw $mini_cmssw $mini_scram_arch
cmsRun $minicfg

setup_cmssw $nano_cmssw $nano_scram_arch
cmsRun $nanocfg

CMSRUN_STATUS=$?

chirp ChirpMetisStatus "after_cmsRun"

echo "after running: ls -lrth"
ls -lrth

if [[ $CMSRUN_STATUS != 0 ]]; then
    echo "Removing output file because cmsRun crashed with exit code $?"
    rm ${OUTPUTNAME}.root
    exit 1
fi


echo -e "\n--- end running ---\n" #                             <----- section division

echo -e "\n--- begin copying output ---\n" #                    <----- section division

echo "Sending output file $OUTPUTNAME.root"

#for nano_file in `ls -1 -d *NanoAOD*.root`; do echo Found nanoAOD output file $nano_file; done
#for nano_file in `ls -1 -d *NanoAOD*.root`; do mv $nano_file output.root; done

if [ ! -e "$OUTPUTNAME.root" ]; then
    echo "ERROR! Output $OUTPUTNAME.root doesn't exist"
    exit 1
fi

echo "time before copy: $(date +%s)"
chirp ChirpMetisStatus "before_copy"

substr="/ceph/cms"
new_OUTPUTDIR=${OUTPUTDIR#$substr}
COPY_SRC="file://`pwd`/${OUTPUTNAME}.root"
COPY_DEST="davs://redirector.t2.ucsd.edu:1095/${new_OUTPUTDIR}/${OUTPUTNAME}_${IFILE}.root"
stageout $COPY_SRC $COPY_DEST
# Copy output
# env -i X509_USER_PROXY=${X509_USER_PROXY} gfal-copy -p -f -t 4200 --verbose file://`pwd`/nanoaod.root davs://redirector.t2.ucsd.edu:1095/${new_OUTPUTDIR}/${OUTPUTFILENAME}_${INDEX}.root --checksum ADLER32


for OTHEROUTPUT in $(echo "$OTHEROUTPUTS" | sed -n 1'p' | tr ',' '\n'); do
    [ -e ${OTHEROUTPUT} ] && {
        NOROOT=$(echo $OTHEROUTPUT | sed 's/\.root//')
        COPY_SRC="file://`pwd`/${NOROOT}.root"
        COPY_DEST="davs://redirector.t2.ucsd.edu:1095/${new_OUTPUTDIR}/${NOROOT}_${IFILE}.root"
        stageout $COPY_SRC $COPY_DEST
    }
done

echo -e "\n--- end copying output ---\n" #                      <----- section division

echo -e "\n--- begin dstat output ---\n" #                      <----- section division
# cat dsout.csv
echo -e "\n--- end dstat output ---\n" #                        <----- section division

echo "time at end: $(date +%s)"

chirp ChirpMetisStatus "done"
