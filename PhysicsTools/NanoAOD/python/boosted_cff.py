import FWCore.ParameterSet.Config as cms
from  PhysicsTools.NanoAOD.common_cff import *
from RecoJets.JetProducers.AnomalousCellParameters_cfi import *
from RecoJets.JetProducers.PFJetParameters_cfi import *
from RecoBTag.SecondaryVertex.pfCombinedInclusiveSecondaryVertexV2BJetTags_cfi import *
from RecoBTag.ImpactParameter.pfImpactParameterTagInfos_cfi import pfImpactParameterTagInfos
from RecoBTag.SecondaryVertex.pfInclusiveSecondaryVertexFinderTagInfos_cfi import *
from RecoBTag.SecondaryVertex.candidateCombinedSecondaryVertexV2Computer_cfi import *
from RecoBTag.SecondaryVertex.pfBoostedDoubleSVAK8TagInfos_cfi import *
from RecoBTag.Configuration.RecoBTag_cff import *
from Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff import *
from Configuration.Geometry.GeometryRecoDB_cff import *
from RecoBTag.Combined.pfDeepCSVJetTags_cfi import pfDeepCSVJetTags
from RecoBTag.SecondaryVertex.combinedSecondaryVertexCommon_cff import combinedSecondaryVertexCommon
from  PhysicsTools.PatAlgos.recoLayer0.jetCorrFactors_cfi import *




##################### User floats producers, selectors ##########################

#Default parameters for HTTV2 and CA15 Fatjets
delta_r = 1.5
jetAlgo = "CambridgeAachen"
subjet_label = "SubJets"
initial_jet = "ca15PFJetsCHS"
maxSVDeltaRToJet = 1.3
weightFile = 'RecoBTag/SecondaryVertex/data/BoostedDoubleSV_CA15_BDT_v3.weights.xml.gz'

######################
####    HTTV2     ####
######################

# Get input objects for HTTV2 calculation
selectedMuonsTmp = cms.EDProducer("MuonRemovalForBoostProducer", 
    src = cms.InputTag("slimmedMuons"),
    vtx = cms.InputTag("offlineSlimmedPrimaryVertices"))
selectedMuons = cms.EDFilter("CandPtrSelector", 
    src = cms.InputTag("selectedMuonsTmp"), 
    cut = cms.string("1"))
selectedElectronsTmp = cms.EDProducer("ElectronRemovalForBoostProducer", 
    src = cms.InputTag("slimmedElectrons"),
    mvaIDMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-tight"),
    rho = cms.InputTag("fixedGridRhoFastjetAll"))
selectedElectrons = cms.EDFilter("CandPtrSelector", 
    src = cms.InputTag("selectedElectronsTmp"), 
    cut = cms.string("1"))
chsTmp1 = cms.EDFilter("CandPtrSelector", 
    src = cms.InputTag("packedPFCandidates"), 
    cut = cms.string("fromPV")) 
chsTmp2 =  cms.EDProducer("CandPtrProjector", 
    src = cms.InputTag("chsTmp1"), 
    veto = cms.InputTag("selectedMuons"))
chs = cms.EDProducer("CandPtrProjector", 
    src = cms.InputTag("chsTmp2"), 
    veto = cms.InputTag("selectedElectrons")) 

#Calculate HTT tagger
looseOptRHTT = cms.EDProducer(
            "HTTTopJetProducer",
            PFJetParameters.clone(
                src               = cms.InputTag("chs"),
                doAreaFastjet     = cms.bool(True),
                doRhoFastjet      = cms.bool(False),
                jetPtMin          = cms.double(200.0)
                ),
            AnomalousCellParameters,
            useExplicitGhosts = cms.bool(True),
            algorithm           = cms.int32(1),
            jetAlgorithm        = cms.string("CambridgeAachen"),
            rParam              = cms.double(1.5),
            optimalR            = cms.bool(True),
            qJets               = cms.bool(False),
            minFatjetPt         = cms.double(200.),
            minSubjetPt         = cms.double(0.),
            minCandPt           = cms.double(0.),
            maxFatjetAbsEta     = cms.double(99.),
            subjetMass          = cms.double(30.),
            muCut               = cms.double(0.8),
            filtR               = cms.double(0.3),
            filtN               = cms.int32(5),
            mode                = cms.int32(4),
            minCandMass         = cms.double(0.),
            maxCandMass         = cms.double(999999.),
            massRatioWidth      = cms.double(999999.),
            minM23Cut           = cms.double(0.),
            minM13Cut           = cms.double(0.),
            maxM13Cut           = cms.double(999999.),
            writeCompound       = cms.bool(True),
            jetCollInstanceName = cms.string("SubJets")
            )

#Calculate subjet btags
looseOptRHTTImpactParameterTagInfos = pfImpactParameterTagInfos.clone(
    primaryVertex = cms.InputTag("offlineSlimmedPrimaryVertices"),
    candidates = cms.InputTag("chs"),
    computeGhostTrack = cms.bool(True),
    computeProbabilities = cms.bool(True),
    maxDeltaR = cms.double(0.4),
    jets = cms.InputTag("looseOptRHTT", "SubJets")
)

looseOptRHTTImpactParameterTagInfos.explicitJTA = cms.bool(True)

looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos = pfInclusiveSecondaryVertexFinderTagInfos.clone(
    extSVCollection = cms.InputTag('slimmedSecondaryVertices'),
    trackIPTagInfos = cms.InputTag("looseOptRHTTImpactParameterTagInfos"),                
)

looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.useSVClustering = cms.bool(True)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.rParam = cms.double(delta_r)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.extSVDeltaRToJet = cms.double(0.3)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.trackSelection.jetDeltaRMax = cms.double(0.3)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.vertexCuts.maxDeltaRToJetAxis = cms.double(0.4)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.jetAlgorithm = cms.string(jetAlgo)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.fatJets  =  cms.InputTag(initial_jet)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.groomedFatJets = cms.InputTag("looseOptRHTT","")

looseOptRHTTpfDeepCSVInfos = pfDeepCSVTagInfos.clone(
    svTagInfos = cms.InputTag("looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos"),
    computer = combinedSecondaryVertexCommon
    )

looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags = pfDeepCSVJetTags.clone(
    src = cms.InputTag('looseOptRHTTpfDeepCSVInfos')
)


jetCorrFactorsHTT = patJetCorrFactors.clone(src=cms.InputTag("looseOptRHTT", "SubJets"),
    levels = cms.vstring('L1FastJet',
        'L2Relative',
        'L3Absolute',
    'L2L3Residual'),
    primaryVertices = cms.InputTag("offlineSlimmedPrimaryVertices"),
)

looseOptRHTTpatSubJets = cms.EDProducer("PATJetProducer",
    jetSource = cms.InputTag("looseOptRHTT", "SubJets"),
    embedPFCandidates = cms.bool(False),
    addJetCorrFactors    = cms.bool(True),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("jetCorrFactorsHTT") ),
    # btag information
    addBTagInfo          = cms.bool(True),   ## master switch
    addDiscriminators    = cms.bool(True),   ## addition btag discriminators
    discriminatorSources = cms.VInputTag(cms.InputTag('looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags', 'probb'),cms.InputTag('looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags', 'probbb')),
    addTagInfos     = cms.bool(False),
    tagInfoSources  = cms.VInputTag(),
    addAssociatedTracks    = cms.bool(False),
    trackAssociationSource = cms.InputTag("ak4JetTracksAssociatorAtVertexPF"),
    addJetCharge    = cms.bool(False),
    jetChargeSource = cms.InputTag("patJetCharge"),
    addJetID = cms.bool(False),
    jetIDMap = cms.InputTag("ak4JetID"),
    addGenPartonMatch   = cms.bool(False),                       
    embedGenPartonMatch = cms.bool(False), 
    genPartonMatch      = cms.InputTag("NOT_IMPLEMENTED"),    
    addGenJetMatch      = cms.bool(False),                       
    embedGenJetMatch    = cms.bool(False),                       
    genJetMatch         = cms.InputTag("NOT_IMPLEMENTED"),     
    addPartonJetMatch   = cms.bool(False),
    partonJetSource     = cms.InputTag("NOT_IMPLEMENTED"),       
    getJetMCFlavour    = cms.bool(False),
    useLegacyJetMCFlavour = cms.bool(False),
    addJetFlavourInfo  = cms.bool(False),
    JetPartonMapSource = cms.InputTag("NOT_IMPLEMENTED"),
    JetFlavourInfoSource = cms.InputTag("NOT_IMPLEMENTED"),
    addEfficiencies = cms.bool(False),
    efficiencies    = cms.PSet(),
    addResolutions = cms.bool(False),
    resolutions     = cms.PSet()
)

#This reorders the subjets as in the original subjet list (ordered by pt in the patjet conversion)
looseOptRHTTSubjetsOrdered =  cms.EDProducer("HTTBtagMatchProducer", 
    jetSource = cms.InputTag("looseOptRHTT", "SubJets"),
    patsubjets = cms.InputTag("looseOptRHTTpatSubJets")
)

#Now, make all the tables
HTTV2Table = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("looseOptRHTT"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("HTTV2"),
    doc  = cms.string("HTTV2 candidates calculated from CA15 fatjets"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars,
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
        subJetIdx1 = Var("?numberOfSourceCandidatePtrs()>0 && sourceCandidatePtr(0).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(0).key():-1", int,
             doc="index of first subjet"),
        subJetIdx2 = Var("?numberOfSourceCandidatePtrs()>1 && sourceCandidatePtr(1).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(1).key():-1", int,
             doc="index of second subjet"),
        subJetIdx3 = Var("?numberOfSourceCandidatePtrs()>2 && sourceCandidatePtr(2).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(2).key():-1", int,
             doc="index of third subjet"),    
    )
)

#Get HTTV2 variables:  fRec,Ropt...
HTTV2InfoTable = cms.EDProducer("SimpleHTTInfoFlatTableProducer",
    src = cms.InputTag("looseOptRHTT"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("HTTV2"),
    doc  = cms.string("Information to HTT candidates"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(True), 
    variables = cms.PSet(
        fRec = Var("abs(properties().fRec())", float, doc="relative W width",precision=10),
        Ropt = Var("properties().ropt()", float, doc="optimal value of R",precision=10),
        RoptCalc = Var("properties().roptCalc()", float, doc="expected value of optimal R",precision=10),
        ptForRoptCalc = Var("properties().ptForRoptCalc()", float, doc="pT used for calculation of RoptCalc",precision=10)
    )
)

#Add HTT subjets
HTTV2SubjetsTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("looseOptRHTTSubjetsOrdered"),
    cut = cms.string(""),
    name = cms.string("HTTV2Subjets"),
    doc  = cms.string("Btags of HTT candidate subjets"),
    singleton = cms.bool(False),
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars,
        IDPassed = Var("?pt() <= 20 || abs(eta()) >= 2.4 || neutralHadronEnergyFraction()>=0.90 || neutralEmEnergyFraction() >= 0.90 ||(chargedMultiplicity()+neutralMultiplicity()) <= 1 || chargedHadronEnergyFraction() <= 0 || chargedMultiplicity() <= 0?0:1",float, doc="Subjet ID passed?",precision=1),
        btag  = Var("bDiscriminator('looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags:probb')+bDiscriminator('looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags:probbb')",float,doc="CSV V2 btag discriminator",precision=10),
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
    )
)



#############################
####    CA15 Fatjets     ####
#############################

ca15PFJetsCHS = cms.EDProducer(
    "FastjetJetProducer",
    PFJetParameters,
    AnomalousCellParameters,
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(1.5))
    
ca15PFJetsCHS.src = cms.InputTag("chs")
ca15PFJetsCHS.jetPtMin = cms.double(200.)


#Hbb tag
ca15PFJetsCHSImpactParameterTagInfos = pfImpactParameterTagInfos.clone(
    primaryVertex = cms.InputTag("offlineSlimmedPrimaryVertices"),
    candidates = cms.InputTag("packedPFCandidates"),
    computeProbabilities = cms.bool(False),
    computeGhostTrack = cms.bool(False),
    maxDeltaR = cms.double(delta_r),
    jets = cms.InputTag("ca15PFJetsCHS"),
)

ca15PFJetsCHSImpactParameterTagInfos.explicitJTA = cms.bool(False)

ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos = pfInclusiveSecondaryVertexFinderTagInfos.clone(
    extSVCollection = cms.InputTag('slimmedSecondaryVertices'),
    trackIPTagInfos = cms.InputTag("ca15PFJetsCHSImpactParameterTagInfos"),                
)

ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.useSVClustering = cms.bool(False)
ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.rParam = cms.double(delta_r)
ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.extSVDeltaRToJet = cms.double(delta_r)
ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.trackSelection.jetDeltaRMax = cms.double(delta_r)
ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.vertexCuts.maxDeltaRToJetAxis = cms.double(delta_r)
ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.jetAlgorithm = cms.string(jetAlgo)

ca15PFJetsCHSpfBoostedDoubleSVTagInfos = pfBoostedDoubleSVAK8TagInfos.clone(
    svTagInfos = cms.InputTag("ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos"),
)

ca15PFJetsCHSpfBoostedDoubleSVTagInfos.trackSelection.jetDeltaRMax = cms.double(delta_r)

ca15PFJetsCHScandidateBoostedDoubleSecondaryVertexComputer = cms.ESProducer("CandidateBoostedDoubleSecondaryVertexESProducer",
   trackSelectionBlock,
   beta = cms.double(1.0),
   R0 = cms.double(delta_r),
   maxSVDeltaRToJet = cms.double(maxSVDeltaRToJet),
   useCondDB = cms.bool(False),
   weightFile = cms.FileInPath(weightFile),
   useGBRForest = cms.bool(True),
   useAdaBoost = cms.bool(False),
   trackPairV0Filter = cms.PSet(k0sMassWindow = cms.double(0.03))
)

ca15PFJetsCHScandidateBoostedDoubleSecondaryVertexComputer.trackSelection.jetDeltaRMax = cms.double(delta_r)

ca15PFJetsCHSpfBoostedDoubleSecondaryVertexBJetTags = cms.EDProducer("JetTagProducer",
    jetTagComputer = cms.string("ca15PFJetsCHScandidateBoostedDoubleSecondaryVertexComputer"),
    tagInfos = cms.VInputTag(cms.InputTag("ca15PFJetsCHSpfBoostedDoubleSVTagInfos"))
)

ca15PFJetsCHSpatFatjet = cms.EDProducer("PATJetProducer",
    jetSource = cms.InputTag("ca15PFJetsCHS"),
    embedPFCandidates = cms.bool(False),
    addJetCorrFactors    = cms.bool(False),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("patJetCorrFactors") ),
    # btag information
    addBTagInfo          = cms.bool(True),   ## master switch
    addDiscriminators    = cms.bool(True),   ## addition btag discriminators
    discriminatorSources = cms.VInputTag(
        cms.InputTag("ca15PFJetsCHSpfBoostedDoubleSecondaryVertexBJetTags"),
    ),
    addTagInfos     = cms.bool(False),
    tagInfoSources  = cms.VInputTag(),
    addAssociatedTracks    = cms.bool(False),
    trackAssociationSource = cms.InputTag("ak4JetTracksAssociatorAtVertexPF"),
    addJetCharge    = cms.bool(False),
    jetChargeSource = cms.InputTag("patJetCharge"),
    addJetID = cms.bool(False),
    jetIDMap = cms.InputTag("ak4JetID"),
    addGenPartonMatch   = cms.bool(False),                           ## switch on/off matching to quarks from hard scatterin
    embedGenPartonMatch = cms.bool(False),                           ## switch on/off embedding of the GenParticle parton for this jet
    genPartonMatch      = cms.InputTag("NOT_IMPLEMENTED"),        ## particles source to be used for the matching
    addGenJetMatch      = cms.bool(False),                           ## switch on/off matching to GenJet's
    embedGenJetMatch    = cms.bool(False),                           ## switch on/off embedding of matched genJet's
    genJetMatch         = cms.InputTag("NOT_IMPLEMENTED"),        ## GenJet source to be used for the matching
    addPartonJetMatch   = cms.bool(False),                          ## switch on/off matching to PartonJet's (not implemented yet)
    partonJetSource     = cms.InputTag("NOT_IMPLEMENTED"),          ## ParticleJet source to be used for the matching
    getJetMCFlavour    = cms.bool(False),
    useLegacyJetMCFlavour = cms.bool(False),
    addJetFlavourInfo  = cms.bool(False),
    JetPartonMapSource = cms.InputTag("NOT_IMPLEMENTED"),
    JetFlavourInfoSource = cms.InputTag("NOT_IMPLEMENTED"),
    addEfficiencies = cms.bool(False),
    efficiencies    = cms.PSet(),
    addResolutions = cms.bool(False),
    resolutions     = cms.PSet()
)

ca15PFJetsCHSFatjetOrdered =  cms.EDProducer("HTTBtagMatchProducer", 
    jetSource = cms.InputTag("ca15PFJetsCHS"),
    patsubjets = cms.InputTag("ca15PFJetsCHSpatFatjet")
)

ca15PFJetsCHSNSubjettiness  = cms.EDProducer("NjettinessAdder",
    src=cms.InputTag("ca15PFJetsCHSFatjetOrdered"),
    cone=cms.double(1.5),
    Njets = cms.vuint32(1,2,3),
    # variables for measure definition : 
    measureDefinition = cms.uint32( 0 ), # CMS default is normalized measure
    beta = cms.double(1.0),              # CMS default is 1
    R0 = cms.double(1.5),                # CMS default is jet cone size
    Rcutoff = cms.double( 999.0),       # not used by default
    # variables for axes definition :
    axesDefinition = cms.uint32( 6 ),    # CMS default is 1-pass KT axes
    nPass = cms.int32(999),             # not used by default
    akAxesR0 = cms.double(-999.0)        # not used by default
)

FatjetsWithUserData = cms.EDProducer("PATJetUserDataEmbedder",
     src = cms.InputTag("ca15PFJetsCHSFatjetOrdered"),
     userFloats = cms.PSet(
        tau1= cms.InputTag("ca15PFJetsCHSNSubjettiness:tau1"),
        tau2= cms.InputTag("ca15PFJetsCHSNSubjettiness:tau2"),
        tau3= cms.InputTag("ca15PFJetsCHSNSubjettiness:tau3"),
     ),
)

finalFatjets = cms.EDFilter("PATJetRefSelector",
    src = cms.InputTag("FatjetsWithUserData"),
    cut = cms.string("pt > 5 ")
)

#Make all tables 
ca15Table = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("ca15PFJetsCHS"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("FatjetCA15"),
    doc  = cms.string("CA15 fatjets (ungroomed)"), 
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars, 
        #jetId = Var("userInt('tightId')*2+userInt('looseId')",int,doc="Jet ID flags bit1 is loose, bit2 is tight"),
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
    )
)

#Add Nsubjettiness and BBtag
FatjetBBTagTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("finalFatjets"),
    cut = cms.string(""),
    name = cms.string("FatjetCA15"),
    doc  = cms.string("CA15 fatjets (ungroomed)"),    
    singleton = cms.bool(False),
    extension = cms.bool(True), 
    variables = cms.PSet(
        bbtag  = Var("bDiscriminator('ca15PFJetsCHSpfBoostedDoubleSecondaryVertexBJetTags')",float,doc="Double btag discriminator",precision=10),
        tau1  = Var("userFloat('tau1')",float,doc="N-subjettiness",precision=10),
        tau2  = Var("userFloat('tau2')",float,doc="N-subjettiness",precision=10),
        tau3  = Var("userFloat('tau3')",float,doc="N-subjettiness",precision=10),
    )
)


######################################
####    CA15 Softdrop Fatjets     ####
######################################

# Apply softdrop to CA R=1.5 jets
ca15PFSoftdropJetsCHS = ca15PFJetsCHS.clone(
    useSoftDrop = cms.bool(True),
    zcut = cms.double(0.1),
    beta = cms.double(0.0),
    R0 = cms.double(1.5),
    useExplicitGhosts = cms.bool(True), 
    writeCompound = cms.bool(True), # Also write subjets
    jetCollInstanceName=cms.string("SubJets"),            
)

#Get Softdrop subjet btags
ca15PFSoftdropJetsCHSImpactParameterTagInfos = pfImpactParameterTagInfos.clone(
    primaryVertex = cms.InputTag("offlineSlimmedPrimaryVertices"),
    candidates = cms.InputTag("chs"),
    computeGhostTrack = cms.bool(True),
    computeProbabilities = cms.bool(True),
    maxDeltaR = cms.double(0.4),
    jets = cms.InputTag("ca15PFSoftdropJetsCHS", "SubJets")
)

ca15PFSoftdropJetsCHSImpactParameterTagInfos.explicitJTA = cms.bool(True)

ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos = pfInclusiveSecondaryVertexFinderTagInfos.clone(
    extSVCollection = cms.InputTag('slimmedSecondaryVertices'),
    trackIPTagInfos = cms.InputTag("ca15PFSoftdropJetsCHSImpactParameterTagInfos"),                
)

ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.useSVClustering = cms.bool(True)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.rParam = cms.double(delta_r)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.extSVDeltaRToJet = cms.double(0.3)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.trackSelection.jetDeltaRMax = cms.double(0.3)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.vertexCuts.maxDeltaRToJetAxis = cms.double(0.4)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.jetAlgorithm = cms.string(jetAlgo)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.fatJets  =  cms.InputTag(initial_jet)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.groomedFatJets = cms.InputTag("ca15PFSoftdropJetsCHS","")


ca15PFSoftdropJetsCHSpfDeepCSVInfos = pfDeepCSVTagInfos.clone(
    svTagInfos = cms.InputTag("ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos"),
    computer = combinedSecondaryVertexCommon
    )

ca15PFSoftdropJetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags = pfDeepCSVJetTags.clone(
    src = cms.InputTag('ca15PFSoftdropJetsCHSpfDeepCSVInfos')
)


jetCorrFactorsSD = patJetCorrFactors.clone(src=cms.InputTag("ca15PFSoftdropJetsCHS", "SubJets"),
    levels = cms.vstring('L1FastJet',
        'L2Relative',
        'L3Absolute',
    'L2L3Residual'),
    primaryVertices = cms.InputTag("offlineSlimmedPrimaryVertices"),
)

ca15PFSoftdropJetsCHSpatSubJets = cms.EDProducer("PATJetProducer",
    jetSource = cms.InputTag("ca15PFSoftdropJetsCHS", "SubJets"),
    embedPFCandidates = cms.bool(False),
    addJetCorrFactors    = cms.bool(True),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("jetCorrFactorsSD") ),
    # btag information
    addBTagInfo          = cms.bool(True),   ## master switch
    addDiscriminators    = cms.bool(True),   ## addition btag discriminators
    discriminatorSources = cms.VInputTag(cms.InputTag('ca15PFSoftdropJetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags', 'probb'),cms.InputTag('ca15PFSoftdropJetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags', 'probbb')),
    addTagInfos     = cms.bool(False),
    tagInfoSources  = cms.VInputTag(),
    addAssociatedTracks    = cms.bool(False),
    trackAssociationSource = cms.InputTag("ak4JetTracksAssociatorAtVertexPF"),
    addJetCharge    = cms.bool(False),
    jetChargeSource = cms.InputTag("patJetCharge"),
    addJetID = cms.bool(False),
    jetIDMap = cms.InputTag("ak4JetID"),
    addGenPartonMatch   = cms.bool(False),                           ## switch on/off matching to quarks from hard scatterin
    embedGenPartonMatch = cms.bool(False),                           ## switch on/off embedding of the GenParticle parton for this jet
    genPartonMatch      = cms.InputTag("patJetPartonMatch"),        ## particles source to be used for the matching
    addGenJetMatch      = cms.bool(False),                           ## switch on/off matching to GenJet's
    embedGenJetMatch    = cms.bool(False),                           ## switch on/off embedding of matched genJet's
    genJetMatch         = cms.InputTag("patJetGenJetMatch"),        ## GenJet source to be used for the matching
    addPartonJetMatch   = cms.bool(False),                          ## switch on/off matching to PartonJet's (not implemented yet)
    partonJetSource     = cms.InputTag("NOT_IMPLEMENTED"),          ## ParticleJet source to be used for the matching
    getJetMCFlavour    = cms.bool(False),
    useLegacyJetMCFlavour = cms.bool(False),
    addJetFlavourInfo  = cms.bool(False),
    JetPartonMapSource = cms.InputTag("patJetFlavourAssociationLegacy"),
    JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociation"),
    addEfficiencies = cms.bool(False),
    efficiencies    = cms.PSet(),
    addResolutions = cms.bool(False),
    resolutions     = cms.PSet()
)

ca15PFSoftdropJetsCHSSubjetsOrdered =  cms.EDProducer("HTTBtagMatchProducer", 
    jetSource = cms.InputTag("ca15PFSoftdropJetsCHS", "SubJets"),
    patsubjets = cms.InputTag("ca15PFSoftdropJetsCHSpatSubJets")
)

#Now get softdrop Hbb and Nsubjettiness

#Need to recreate softdrop jets without subjets to get jet constituents.
ca15PFSoftdropJetsCHSNoSub = ca15PFJetsCHS.clone(
    useSoftDrop = cms.bool(True),
    zcut = cms.double(0.1),
    beta = cms.double(0.0),
    R0 = cms.double(1.5),
    useExplicitGhosts = cms.bool(True),            
)


ca15PFSDJetsCHSImpactParameterTagInfos = pfImpactParameterTagInfos.clone(
    primaryVertex = cms.InputTag("offlineSlimmedPrimaryVertices"),
    candidates = cms.InputTag("packedPFCandidates"),
    computeProbabilities = cms.bool(False),
    computeGhostTrack = cms.bool(False),
    maxDeltaR = cms.double(delta_r),
    jets = cms.InputTag("ca15PFSoftdropJetsCHSNoSub"),
)

ca15PFSDJetsCHSImpactParameterTagInfos.explicitJTA = cms.bool(False)

ca15PFSDJetsCHSpfInclusiveSecondaryVertexFinderTagInfos = pfInclusiveSecondaryVertexFinderTagInfos.clone(
    extSVCollection = cms.InputTag('slimmedSecondaryVertices'),
    trackIPTagInfos = cms.InputTag("ca15PFSDJetsCHSImpactParameterTagInfos"),                
)

ca15PFSDJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.useSVClustering = cms.bool(False)
ca15PFSDJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.rParam = cms.double(delta_r)
ca15PFSDJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.extSVDeltaRToJet = cms.double(delta_r)
ca15PFSDJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.trackSelection.jetDeltaRMax = cms.double(delta_r)
ca15PFSDJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.vertexCuts.maxDeltaRToJetAxis = cms.double(delta_r)
ca15PFSDJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.jetAlgorithm = cms.string(jetAlgo)

ca15PFSDJetsCHSpfBoostedDoubleSVTagInfos = pfBoostedDoubleSVAK8TagInfos.clone(
    svTagInfos = cms.InputTag("ca15PFSDJetsCHSpfInclusiveSecondaryVertexFinderTagInfos"),
)

ca15PFSDJetsCHSpfBoostedDoubleSVTagInfos.trackSelection.jetDeltaRMax = cms.double(delta_r)

ca15PFSDJetsCHScandidateBoostedDoubleSecondaryVertexComputer = cms.ESProducer("CandidateBoostedDoubleSecondaryVertexESProducer",
   trackSelectionBlock,
   beta = cms.double(1.0),
   R0 = cms.double(delta_r),
   maxSVDeltaRToJet = cms.double(maxSVDeltaRToJet),
   useCondDB = cms.bool(False),
   weightFile = cms.FileInPath(weightFile),
   useGBRForest = cms.bool(True),
   useAdaBoost = cms.bool(False),
   trackPairV0Filter = cms.PSet(k0sMassWindow = cms.double(0.03))
)

ca15PFSDJetsCHScandidateBoostedDoubleSecondaryVertexComputer.trackSelection.jetDeltaRMax = cms.double(delta_r)

ca15PFSDJetsCHSpfBoostedDoubleSecondaryVertexBJetTags = cms.EDProducer("JetTagProducer",
    jetTagComputer = cms.string("ca15PFSDJetsCHScandidateBoostedDoubleSecondaryVertexComputer"),
    tagInfos = cms.VInputTag(cms.InputTag("ca15PFSDJetsCHSpfBoostedDoubleSVTagInfos"))
)

ca15PFSDJetsCHSpatFatjet = cms.EDProducer("PATJetProducer",
    jetSource = cms.InputTag("ca15PFSoftdropJetsCHSNoSub"),
    embedPFCandidates = cms.bool(False),
    addJetCorrFactors    = cms.bool(False),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("patJetCorrFactors") ),
    # btag information
    addBTagInfo          = cms.bool(True),   ## master switch
    addDiscriminators    = cms.bool(True),   ## addition btag discriminators
    discriminatorSources = cms.VInputTag(
        cms.InputTag("ca15PFSDJetsCHSpfBoostedDoubleSecondaryVertexBJetTags"),
    ),
    addTagInfos     = cms.bool(False),
    tagInfoSources  = cms.VInputTag(),
    addAssociatedTracks    = cms.bool(False),
    trackAssociationSource = cms.InputTag("ak4JetTracksAssociatorAtVertexPF"),
    addJetCharge    = cms.bool(False),
    jetChargeSource = cms.InputTag("patJetCharge"),
    addJetID = cms.bool(False),
    jetIDMap = cms.InputTag("ak4JetID"),
    addGenPartonMatch   = cms.bool(False),                           ## switch on/off matching to quarks from hard scatterin
    embedGenPartonMatch = cms.bool(False),                           ## switch on/off embedding of the GenParticle parton for this jet
    genPartonMatch      = cms.InputTag("NOT_IMPLEMENTED"),        ## particles source to be used for the matching
    addGenJetMatch      = cms.bool(False),                           ## switch on/off matching to GenJet's
    embedGenJetMatch    = cms.bool(False),                           ## switch on/off embedding of matched genJet's
    genJetMatch         = cms.InputTag("NOT_IMPLEMENTED"),        ## GenJet source to be used for the matching
    addPartonJetMatch   = cms.bool(False),                          ## switch on/off matching to PartonJet's (not implemented yet)
    partonJetSource     = cms.InputTag("NOT_IMPLEMENTED"),          ## ParticleJet source to be used for the matching
    getJetMCFlavour    = cms.bool(False),
    useLegacyJetMCFlavour = cms.bool(False),
    addJetFlavourInfo  = cms.bool(False),
    JetPartonMapSource = cms.InputTag("NOT_IMPLEMENTED"),
    JetFlavourInfoSource = cms.InputTag("NOT_IMPLEMENTED"),
    addEfficiencies = cms.bool(False),
    efficiencies    = cms.PSet(),
    addResolutions = cms.bool(False),
    resolutions     = cms.PSet()
)

ca15PFSDJetsCHSFatjetOrdered =  cms.EDProducer("HTTBtagMatchProducer", 
    jetSource = cms.InputTag("ca15PFSoftdropJetsCHSNoSub"),
    patsubjets = cms.InputTag("ca15PFSDJetsCHSpatFatjet")
)

ca15PFSDJetsCHSNSubjettiness  = cms.EDProducer("NjettinessAdder",
    src=cms.InputTag("ca15PFSDJetsCHSFatjetOrdered"),
    cone=cms.double(1.5),
    Njets = cms.vuint32(1,2,3),
    # variables for measure definition : 
    measureDefinition = cms.uint32( 0 ), # CMS default is normalized measure
    beta = cms.double(1.0),              # CMS default is 1
    R0 = cms.double(1.5),                # CMS default is jet cone size
    Rcutoff = cms.double( 999.0),       # not used by default
    # variables for axes definition :
    axesDefinition = cms.uint32( 6 ),    # CMS default is 1-pass KT axes
    nPass = cms.int32(999),             # not used by default
    akAxesR0 = cms.double(-999.0)        # not used by default
)

SDFatjetsWithUserData = cms.EDProducer("PATJetUserDataEmbedder",
     src = cms.InputTag("ca15PFSDJetsCHSFatjetOrdered"),
     userFloats = cms.PSet(
        tau1= cms.InputTag("ca15PFSDJetsCHSNSubjettiness:tau1"),
        tau2= cms.InputTag("ca15PFSDJetsCHSNSubjettiness:tau2"),
        tau3= cms.InputTag("ca15PFSDJetsCHSNSubjettiness:tau3"),
     ),
)

finalSDFatjets = cms.EDFilter("PATJetRefSelector",
    src = cms.InputTag("SDFatjetsWithUserData"),
    cut = cms.string("pt > 5 ")
)

#Make all tables
ca15SoftDropTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("ca15PFSoftdropJetsCHS"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("FatjetCA15SoftDrop"),
    doc  = cms.string("Softdrop CA15 fatjets (zcut = 0.1, beta = 0)"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars, 
        #jetId = Var("userInt('tightId')*2+userInt('looseId')",int,doc="Jet ID flags bit1 is loose, bit2 is tight"),
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
        subJetIdx1 = Var("?numberOfSourceCandidatePtrs()>0 && sourceCandidatePtr(0).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(0).key():-1", int,
             doc="index of first subjet"),
        subJetIdx2 = Var("?numberOfSourceCandidatePtrs()>1 && sourceCandidatePtr(1).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(1).key():-1", int,
             doc="index of second subjet"),    
    )
)

#Add Nsubjettiness and BBtag
SDFatjetBBTagTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("finalSDFatjets"),
    cut = cms.string(""),
    name = cms.string("FatjetCA15SoftDrop"),
    doc  = cms.string("Softdrop CA15 fatjets (zcut = 0.1, beta = 0)"),    
    singleton = cms.bool(False),
    extension = cms.bool(True), 
    variables = cms.PSet(
        bbtag  = Var("bDiscriminator('ca15PFSDJetsCHSpfBoostedDoubleSecondaryVertexBJetTags')",float,doc="Double btag discriminator",precision=10),
        tau1  = Var("userFloat('tau1')",float,doc="N-subjettiness",precision=10),
        tau2  = Var("userFloat('tau2')",float,doc="N-subjettiness",precision=10),
        tau3  = Var("userFloat('tau3')",float,doc="N-subjettiness",precision=10),
    )
)

ca15SoftDropSubjetsTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("ca15PFSoftdropJetsCHSSubjetsOrdered"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("FatjetCA15SoftDropSubjets"),
    doc  = cms.string("Softdrop CA15 subjets (zcut = 0.1, beta = 0)"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars, 
        #jetId = Var("userInt('tightId')*2+userInt('looseId')",int,doc="Jet ID flags bit1 is loose, bit2 is tight"),
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
        btag  = Var("bDiscriminator('ca15PFSoftdropJetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags:probb')+bDiscriminator('ca15PFSoftdropJetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags:probbb')",float,doc="CMVA V2 btag discriminator",precision=10),
        IDPassed = Var("?pt() <= 20 || abs(eta()) >= 2.4 || neutralHadronEnergyFraction()>=0.90 || neutralEmEnergyFraction() >= 0.90 ||(chargedMultiplicity()+neutralMultiplicity()) <= 1 || chargedHadronEnergyFraction() <= 0 || chargedMultiplicity() <= 0?0:1",float, doc="Subjet ID passed?",precision=1),
    )
)

######################################################
####    CA15 Softdrop Fatjets (beta=1, z=0.2)     ####
######################################################

# Apply softdrop to CA R=1.5 jets
ca15PFSoftdrop2JetsCHS = ca15PFJetsCHS.clone(
    useSoftDrop = cms.bool(True),
    zcut = cms.double(0.2),
    beta = cms.double(1.0),
    R0 = cms.double(1.5),
    useExplicitGhosts = cms.bool(True), 
    writeCompound = cms.bool(True), # Also write subjets
    jetCollInstanceName=cms.string("SubJets"),            
)

#Get Softdrop subjet btags
ca15PFSoftdrop2JetsCHSImpactParameterTagInfos = pfImpactParameterTagInfos.clone(
    primaryVertex = cms.InputTag("offlineSlimmedPrimaryVertices"),
    candidates = cms.InputTag("chs"),
    computeGhostTrack = cms.bool(True),
    computeProbabilities = cms.bool(True),
    maxDeltaR = cms.double(0.4),
    jets = cms.InputTag("ca15PFSoftdrop2JetsCHS", "SubJets")
)

ca15PFSoftdrop2JetsCHSImpactParameterTagInfos.explicitJTA = cms.bool(True)

ca15PFSoftdrop2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos = pfInclusiveSecondaryVertexFinderTagInfos.clone(
    extSVCollection = cms.InputTag('slimmedSecondaryVertices'),
    trackIPTagInfos = cms.InputTag("ca15PFSoftdrop2JetsCHSImpactParameterTagInfos"),                
)

ca15PFSoftdrop2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.useSVClustering = cms.bool(True)
ca15PFSoftdrop2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.rParam = cms.double(delta_r)
ca15PFSoftdrop2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.extSVDeltaRToJet = cms.double(0.3)
ca15PFSoftdrop2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.trackSelection.jetDeltaRMax = cms.double(0.3)
ca15PFSoftdrop2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.vertexCuts.maxDeltaRToJetAxis = cms.double(0.4)
ca15PFSoftdrop2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.jetAlgorithm = cms.string(jetAlgo)
ca15PFSoftdrop2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.fatJets  =  cms.InputTag(initial_jet)
ca15PFSoftdrop2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.groomedFatJets = cms.InputTag("ca15PFSoftdrop2JetsCHS","")


ca15PFSoftdrop2JetsCHSpfDeepCSVInfos = pfDeepCSVTagInfos.clone(
    svTagInfos = cms.InputTag("ca15PFSoftdrop2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos"),
    computer = combinedSecondaryVertexCommon
    )

ca15PFSoftdrop2JetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags = pfDeepCSVJetTags.clone(
    src = cms.InputTag('ca15PFSoftdrop2JetsCHSpfDeepCSVInfos')
)


jetCorrFactorsSD2 = patJetCorrFactors.clone(src=cms.InputTag("ca15PFSoftdrop2JetsCHS", "SubJets"),
    levels = cms.vstring('L1FastJet',
        'L2Relative',
        'L3Absolute',
    'L2L3Residual'),
    primaryVertices = cms.InputTag("offlineSlimmedPrimaryVertices"),
)


ca15PFSoftdrop2JetsCHSpatSubJets = cms.EDProducer("PATJetProducer",
    jetSource = cms.InputTag("ca15PFSoftdrop2JetsCHS", "SubJets"),
    embedPFCandidates = cms.bool(False),
    addJetCorrFactors    = cms.bool(True),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("jetCorrFactorsSD2") ),
    # btag information
    addBTagInfo          = cms.bool(True),   ## master switch
    addDiscriminators    = cms.bool(True),   ## addition btag discriminators
    discriminatorSources = cms.VInputTag(cms.InputTag('ca15PFSoftdrop2JetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags', 'probb'),cms.InputTag('ca15PFSoftdrop2JetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags', 'probbb')),
    addTagInfos     = cms.bool(False),
    tagInfoSources  = cms.VInputTag(),
    addAssociatedTracks    = cms.bool(False),
    trackAssociationSource = cms.InputTag("ak4JetTracksAssociatorAtVertexPF"),
    addJetCharge    = cms.bool(False),
    jetChargeSource = cms.InputTag("patJetCharge"),
    addJetID = cms.bool(False),
    jetIDMap = cms.InputTag("ak4JetID"),
    addGenPartonMatch   = cms.bool(False),                           ## switch on/off matching to quarks from hard scatterin
    embedGenPartonMatch = cms.bool(False),                           ## switch on/off embedding of the GenParticle parton for this jet
    genPartonMatch      = cms.InputTag("patJetPartonMatch"),        ## particles source to be used for the matching
    addGenJetMatch      = cms.bool(False),                           ## switch on/off matching to GenJet's
    embedGenJetMatch    = cms.bool(False),                           ## switch on/off embedding of matched genJet's
    genJetMatch         = cms.InputTag("patJetGenJetMatch"),        ## GenJet source to be used for the matching
    addPartonJetMatch   = cms.bool(False),                          ## switch on/off matching to PartonJet's (not implemented yet)
    partonJetSource     = cms.InputTag("NOT_IMPLEMENTED"),          ## ParticleJet source to be used for the matching
    getJetMCFlavour    = cms.bool(False),
    useLegacyJetMCFlavour = cms.bool(False),
    addJetFlavourInfo  = cms.bool(False),
    JetPartonMapSource = cms.InputTag("patJetFlavourAssociationLegacy"),
    JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociation"),
    addEfficiencies = cms.bool(False),
    efficiencies    = cms.PSet(),
    addResolutions = cms.bool(False),
    resolutions     = cms.PSet()
)

ca15PFSoftdrop2JetsCHSSubjetsOrdered =  cms.EDProducer("HTTBtagMatchProducer", 
    jetSource = cms.InputTag("ca15PFSoftdrop2JetsCHS", "SubJets"),
    patsubjets = cms.InputTag("ca15PFSoftdrop2JetsCHSpatSubJets")
)

#Now get softdrop Hbb and Nsubjettiness

#Need to recreate softdrop jets without subjets to get jet constituents.
ca15PFSoftdrop2JetsCHSNoSub = ca15PFJetsCHS.clone(
    useSoftDrop = cms.bool(True),
    zcut = cms.double(0.2),
    beta = cms.double(1.0),
    R0 = cms.double(1.5),
    useExplicitGhosts = cms.bool(True),            
)

ca15PFSD2JetsCHSImpactParameterTagInfos = pfImpactParameterTagInfos.clone(
    primaryVertex = cms.InputTag("offlineSlimmedPrimaryVertices"),
    candidates = cms.InputTag("packedPFCandidates"),
    computeProbabilities = cms.bool(False),
    computeGhostTrack = cms.bool(False),
    maxDeltaR = cms.double(delta_r),
    jets = cms.InputTag("ca15PFSoftdrop2JetsCHSNoSub"),
)

ca15PFSD2JetsCHSImpactParameterTagInfos.explicitJTA = cms.bool(False)

ca15PFSD2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos = pfInclusiveSecondaryVertexFinderTagInfos.clone(
    extSVCollection = cms.InputTag('slimmedSecondaryVertices'),
    trackIPTagInfos = cms.InputTag("ca15PFSD2JetsCHSImpactParameterTagInfos"),                
)

ca15PFSD2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.useSVClustering = cms.bool(False)
ca15PFSD2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.rParam = cms.double(delta_r)
ca15PFSD2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.extSVDeltaRToJet = cms.double(delta_r)
ca15PFSD2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.trackSelection.jetDeltaRMax = cms.double(delta_r)
ca15PFSD2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.vertexCuts.maxDeltaRToJetAxis = cms.double(delta_r)
ca15PFSD2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos.jetAlgorithm = cms.string(jetAlgo)

ca15PFSD2JetsCHSpfBoostedDoubleSVTagInfos = pfBoostedDoubleSVAK8TagInfos.clone(
    svTagInfos = cms.InputTag("ca15PFSD2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos"),
)

ca15PFSD2JetsCHSpfBoostedDoubleSVTagInfos.trackSelection.jetDeltaRMax = cms.double(delta_r)

ca15PFSD2JetsCHScandidateBoostedDoubleSecondaryVertexComputer = cms.ESProducer("CandidateBoostedDoubleSecondaryVertexESProducer",
   trackSelectionBlock,
   beta = cms.double(1.0),
   R0 = cms.double(delta_r),
   maxSVDeltaRToJet = cms.double(maxSVDeltaRToJet),
   useCondDB = cms.bool(False),
   weightFile = cms.FileInPath(weightFile),
   useGBRForest = cms.bool(True),
   useAdaBoost = cms.bool(False),
   trackPairV0Filter = cms.PSet(k0sMassWindow = cms.double(0.03))
)

ca15PFSD2JetsCHScandidateBoostedDoubleSecondaryVertexComputer.trackSelection.jetDeltaRMax = cms.double(delta_r)

ca15PFSD2JetsCHSpfBoostedDoubleSecondaryVertexBJetTags = cms.EDProducer("JetTagProducer",
    jetTagComputer = cms.string("ca15PFSD2JetsCHScandidateBoostedDoubleSecondaryVertexComputer"),
    tagInfos = cms.VInputTag(cms.InputTag("ca15PFSD2JetsCHSpfBoostedDoubleSVTagInfos"))
)

ca15PFSD2JetsCHSpatFatjet = cms.EDProducer("PATJetProducer",
    jetSource = cms.InputTag("ca15PFSoftdrop2JetsCHSNoSub"),
    embedPFCandidates = cms.bool(False),
    addJetCorrFactors    = cms.bool(False),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("patJetCorrFactors") ),
    # btag information
    addBTagInfo          = cms.bool(True),   ## master switch
    addDiscriminators    = cms.bool(True),   ## addition btag discriminators
    discriminatorSources = cms.VInputTag(
        cms.InputTag("ca15PFSD2JetsCHSpfBoostedDoubleSecondaryVertexBJetTags"),
    ),
    addTagInfos     = cms.bool(False),
    tagInfoSources  = cms.VInputTag(),
    addAssociatedTracks    = cms.bool(False),
    trackAssociationSource = cms.InputTag("ak4JetTracksAssociatorAtVertexPF"),
    addJetCharge    = cms.bool(False),
    jetChargeSource = cms.InputTag("patJetCharge"),
    addJetID = cms.bool(False),
    jetIDMap = cms.InputTag("ak4JetID"),
    addGenPartonMatch   = cms.bool(False),                           ## switch on/off matching to quarks from hard scatterin
    embedGenPartonMatch = cms.bool(False),                           ## switch on/off embedding of the GenParticle parton for this jet
    genPartonMatch      = cms.InputTag("NOT_IMPLEMENTED"),        ## particles source to be used for the matching
    addGenJetMatch      = cms.bool(False),                           ## switch on/off matching to GenJet's
    embedGenJetMatch    = cms.bool(False),                           ## switch on/off embedding of matched genJet's
    genJetMatch         = cms.InputTag("NOT_IMPLEMENTED"),        ## GenJet source to be used for the matching
    addPartonJetMatch   = cms.bool(False),                          ## switch on/off matching to PartonJet's (not implemented yet)
    partonJetSource     = cms.InputTag("NOT_IMPLEMENTED"),          ## ParticleJet source to be used for the matching
    getJetMCFlavour    = cms.bool(False),
    useLegacyJetMCFlavour = cms.bool(False),
    addJetFlavourInfo  = cms.bool(False),
    JetPartonMapSource = cms.InputTag("NOT_IMPLEMENTED"),
    JetFlavourInfoSource = cms.InputTag("NOT_IMPLEMENTED"),
    addEfficiencies = cms.bool(False),
    efficiencies    = cms.PSet(),
    addResolutions = cms.bool(False),
    resolutions     = cms.PSet()
)

ca15PFSD2JetsCHSFatjetOrdered =  cms.EDProducer("HTTBtagMatchProducer", 
    jetSource = cms.InputTag("ca15PFSoftdrop2JetsCHSNoSub"),
    patsubjets = cms.InputTag("ca15PFSD2JetsCHSpatFatjet")
)

ca15PFSD2JetsCHSNSubjettiness  = cms.EDProducer("NjettinessAdder",
    src=cms.InputTag("ca15PFSD2JetsCHSFatjetOrdered"),
    cone=cms.double(1.5),
    Njets = cms.vuint32(1,2,3),
    # variables for measure definition : 
    measureDefinition = cms.uint32( 0 ), # CMS default is normalized measure
    beta = cms.double(1.0),              # CMS default is 1
    R0 = cms.double(1.5),                # CMS default is jet cone size
    Rcutoff = cms.double( 999.0),       # not used by default
    # variables for axes definition :
    axesDefinition = cms.uint32( 6 ),    # CMS default is 1-pass KT axes
    nPass = cms.int32(999),             # not used by default
    akAxesR0 = cms.double(-999.0)        # not used by default
)

SD2FatjetsWithUserData = cms.EDProducer("PATJetUserDataEmbedder",
     src = cms.InputTag("ca15PFSD2JetsCHSFatjetOrdered"),
     userFloats = cms.PSet(
        tau1= cms.InputTag("ca15PFSD2JetsCHSNSubjettiness:tau1"),
        tau2= cms.InputTag("ca15PFSD2JetsCHSNSubjettiness:tau2"),
        tau3= cms.InputTag("ca15PFSD2JetsCHSNSubjettiness:tau3"),
     ),
)

finalSD2Fatjets = cms.EDFilter("PATJetRefSelector",
    src = cms.InputTag("SD2FatjetsWithUserData"),
    cut = cms.string("pt > 5 ")
)

#Make all tables
ca15SoftDrop2Table = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("ca15PFSoftdrop2JetsCHS"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("FatjetCA15SoftDrop_b1z02"),
    doc  = cms.string("Softdrop CA15 fatjets (zcut = 0.2, beta = 1)"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars, 
        #jetId = Var("userInt('tightId')*2+userInt('looseId')",int,doc="Jet ID flags bit1 is loose, bit2 is tight"),
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
        subJetIdx1 = Var("?numberOfSourceCandidatePtrs()>0 && sourceCandidatePtr(0).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(0).key():-1", int,
             doc="index of first subjet"),
        subJetIdx2 = Var("?numberOfSourceCandidatePtrs()>1 && sourceCandidatePtr(1).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(1).key():-1", int,
             doc="index of second subjet"),    
    )
)

#Add Nsubjettiness and BBtag
SD2FatjetBBTagTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("finalSD2Fatjets"),
    cut = cms.string(""),
    name = cms.string("FatjetCA15SoftDrop_b1z02"),
    doc  = cms.string("Softdrop CA15 fatjets (zcut = 0.2, beta = 1)"),
    singleton = cms.bool(False),
    extension = cms.bool(True), 
    variables = cms.PSet(
        bbtag  = Var("bDiscriminator('ca15PFSD2JetsCHSpfBoostedDoubleSecondaryVertexBJetTags')",float,doc="Double btag discriminator",precision=10),
        tau1  = Var("userFloat('tau1')",float,doc="N-subjettiness",precision=10),
        tau2  = Var("userFloat('tau2')",float,doc="N-subjettiness",precision=10),
        tau3  = Var("userFloat('tau3')",float,doc="N-subjettiness",precision=10),
    )
)

ca15SoftDrop2SubjetsTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("ca15PFSoftdrop2JetsCHSSubjetsOrdered"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("FatjetCA15SoftDropSubjets_b1z02"),
    doc  = cms.string("Softdrop CA15 subjets (zcut = 0.2, beta = 1)"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars, 
        #jetId = Var("userInt('tightId')*2+userInt('looseId')",int,doc="Jet ID flags bit1 is loose, bit2 is tight"),
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
        btag  = Var("bDiscriminator('ca15PFSoftdrop2JetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags:probb')+bDiscriminator('ca15PFSoftdrop2JetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags:probbb')",float,doc="CMVA V2 btag discriminator",precision=10),
        IDPassed = Var("?pt() <= 20 || abs(eta()) >= 2.4 || neutralHadronEnergyFraction()>=0.90 || neutralEmEnergyFraction() >= 0.90 ||(chargedMultiplicity()+neutralMultiplicity()) <= 1 || chargedHadronEnergyFraction() <= 0 || chargedMultiplicity() <= 0?0:1",float, doc="Subjet ID passed?",precision=1),
    )
)

boostedSequence = cms.Sequence(
    #Prepare input objects
    selectedMuonsTmp+selectedMuons+selectedElectronsTmp+selectedElectrons+chsTmp1+chsTmp2+chs+ca15PFJetsCHS+ \
    #HTTV2 + subjet btags
    looseOptRHTT+looseOptRHTTImpactParameterTagInfos+looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos+ \
    looseOptRHTTpfDeepCSVInfos +\
    looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags+jetCorrFactorsHTT+looseOptRHTTpatSubJets+looseOptRHTTSubjetsOrdered+ \
    #CA15 double btag
    ca15PFJetsCHSImpactParameterTagInfos+ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos+ \
    ca15PFJetsCHSpfBoostedDoubleSVTagInfos+ca15PFJetsCHSpfBoostedDoubleSecondaryVertexBJetTags+ \
    ca15PFJetsCHSpatFatjet+ca15PFJetsCHSFatjetOrdered+ca15PFJetsCHSNSubjettiness+FatjetsWithUserData+finalFatjets+ \
    #Softdrop CA15 jets + subjet btags
    ca15PFSoftdropJetsCHS+ca15PFSoftdropJetsCHSImpactParameterTagInfos+ ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos+ \
    ca15PFSoftdropJetsCHSpfDeepCSVInfos+ \
    ca15PFSoftdropJetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags+jetCorrFactorsSD+\
    ca15PFSoftdropJetsCHSpatSubJets+ca15PFSoftdropJetsCHSSubjetsOrdered + \
    #Softdrop bbtag + nsubjettiness
    ca15PFSoftdropJetsCHSNoSub+ca15PFSDJetsCHSImpactParameterTagInfos+ca15PFSDJetsCHSpfInclusiveSecondaryVertexFinderTagInfos+ \
    ca15PFSDJetsCHSpfBoostedDoubleSVTagInfos+ca15PFSDJetsCHSpfBoostedDoubleSecondaryVertexBJetTags+\
    ca15PFSDJetsCHSpatFatjet+ca15PFSDJetsCHSFatjetOrdered+ca15PFSDJetsCHSNSubjettiness+SDFatjetsWithUserData+finalSDFatjets +\
    #Softdrop beta = 1, zcut = 0.2
    ca15PFSoftdrop2JetsCHS+ca15PFSoftdrop2JetsCHSImpactParameterTagInfos+ ca15PFSoftdrop2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos+ \
    ca15PFSoftdrop2JetsCHSpfDeepCSVInfos+ \
    ca15PFSoftdrop2JetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags+ jetCorrFactorsSD2+\
    ca15PFSoftdrop2JetsCHSpatSubJets+ca15PFSoftdrop2JetsCHSSubjetsOrdered + \
    #Softdrop bbtag + nsubjettiness
    ca15PFSoftdrop2JetsCHSNoSub+ca15PFSD2JetsCHSImpactParameterTagInfos+ca15PFSD2JetsCHSpfInclusiveSecondaryVertexFinderTagInfos+ \
    ca15PFSD2JetsCHSpfBoostedDoubleSVTagInfos+ca15PFSD2JetsCHSpfBoostedDoubleSecondaryVertexBJetTags+\
    ca15PFSD2JetsCHSpatFatjet+ca15PFSD2JetsCHSFatjetOrdered+ca15PFSD2JetsCHSNSubjettiness+SD2FatjetsWithUserData+finalSD2Fatjets

)
boostedTables = cms.Sequence(HTTV2Table+HTTV2InfoTable+HTTV2SubjetsTable+ \
    ca15Table+FatjetBBTagTable+ca15SoftDropTable+SDFatjetBBTagTable+ca15SoftDropSubjetsTable+\
    ca15SoftDrop2Table+SD2FatjetBBTagTable+ca15SoftDrop2SubjetsTable)

