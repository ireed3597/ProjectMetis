# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: Configuration/GenProduction/python/HIG-RunIISummer19UL18GEN-00004-fragment.py --python_filename HIG-RunIISummer19UL18GEN-00004_1_cfg.py --eventcontent RAWSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN --fileout file:HIG-RunIISummer19UL18GEN-00004.root --conditions 106X_upgrade2018_realistic_v4 --beamspot Realistic25ns13TeVEarly2018Collision --step GEN --geometry DB:Extended --era Run2_2018 --no_exec --mc -n 7089
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2018_cff import Run2_2018

process = cms.Process('GEN',Run2_2018)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic25ns13TeVEarly2018Collision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(7089)
)

# Input source
process.source = cms.Source("EmptySource")

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('Configuration/GenProduction/python/HIG-RunIISummer19UL18GEN-00004-fragment.py nevts:7089'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.RAWSIMoutput = cms.OutputModule("PoolOutputModule",
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('generation_step')
    ),
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(1),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN'),
        filterName = cms.untracked.string('')
    ),
    eventAutoFlushCompressedSize = cms.untracked.int32(20971520),
    # fileName = cms.untracked.string('file:HIG-RunIISummer19UL18GEN-00004.root'),
    fileName = cms.untracked.string('file:file:HIG-RunIISummer20UL18wmLHEGEN-03457.root'),#just to keep the chain psets unchanged
    
    outputCommands = process.RAWSIMEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

# Additional output definition

# Other statements
process.genstepfilter.triggerConditions=cms.vstring("generation_step")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2018_realistic_v4', '')

process.generator = cms.EDFilter("SherpaGeneratorFilter",
    FetchSherpack = cms.bool(True),
    SherpaDefaultWeight = cms.double(1.0),
    SherpaParameters = cms.PSet(
        MPI_Cross_Sections = cms.vstring(
            ' MPIs in Sherpa, Model = Amisic:', 
            ' semihard xsec = 39.9435 mb,', 
            ' non-diffractive xsec = 17.0318 mb with nd factor = 0.3142.'
        ),
        Run = cms.vstring(
            ' (run){', 
            ' EVENTS 1000;', 
            ' EVENT_MODE HepMC;', 
            ' ME_SIGNAL_GENERATOR Comix Internal;',
            ' EVENT_GENERATION_MODE Unweighted;', 
            ' BEAM_1 2212; BEAM_ENERGY_1 6500.;', 
            ' BEAM_2 2212; BEAM_ENERGY_2 6500.;', 
            ' PDF_LIBRARY     LHAPDFSherpa;', 
            ' PDF_SET         NNPDF30_nnlo_as_0118;', 
            ' PDF_SET_VERSION 0;', 
            ' PDF_GRID_PATH   PDFsets;', 
            ' CSS_EW_MODE 1;', 
            ' ME_QED Off;', 
            '}(run)', 
            ' (processes){', 
            ' Process 21 21 -> 22 22;', 
            ' Scales VAR{Abs2(p[2]+p[3])};', 
            ' ME_Generator Internal;', 
            ' Loop_Generator gg_yy;', 
            ' End process;', 
            ' Process 93 93 -> 22 22 93{3};', 
            ' Order (*,2);', 
            ' Enhance_Factor 2 {3};', 
            ' Enhance_Factor 5 {4};', 
            ' Enhance_Factor 10 {5};', 
            ' CKKW sqr(20./E_CMS);', 
            ' Integration_Error 0.005 {3};', 
            ' Integration_Error 0.03 {4};', 
            ' Integration_Error 0.05 {5};', 
            ' End process;', 
            '}(processes)', 
            ' (selector){', 
            ' Mass  22 22 40. 80.;', 
            ' PT 22 10. E_CMS;', 
            '}(selector)'
        ),
        parameterSets = cms.vstring(
            'MPI_Cross_Sections', 
            'Run'
        )
    ),
    SherpaPath = cms.string('./'),
    SherpaProcess = cms.string('sherpa_13TeV_gamgam_3j_loop_Mgg40-80'),
    SherpaResultDir = cms.string('Result'),
    SherpackChecksum = cms.string('c5d34393428c3b197399fd196b4487bd'),
    SherpackLocation = cms.string('/cvmfs/cms.cern.ch/phys_generator/gridpacks/2017/13TeV/sherpa/V2.2.5/sherpa_13TeV_3j_Mgg40-80-13000_MASTER/v1'),
    crossSection = cms.untracked.double(-1),
    filterEfficiency = cms.untracked.double(1.0),
    maxEventsToPrint = cms.int32(0)
)


process.ProductionFilterSequence = cms.Sequence(process.generator)

# Path and EndPath definitions
process.generation_step = cms.Path(process.pgen)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RAWSIMoutput_step = cms.EndPath(process.RAWSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.generation_step,process.genfiltersummary_step,process.endjob_step,process.RAWSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
# filter all path with the production filter sequence
for path in process.paths:
	getattr(process,path).insert(0, process.ProductionFilterSequence)

# customisation of the process.

# Automatic addition of the customisation function from Configuration.DataProcessing.Utils
from Configuration.DataProcessing.Utils import addMonitoring 

#call to customisation function addMonitoring imported from Configuration.DataProcessing.Utils
process = addMonitoring(process)

# End of customisation functions

# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
