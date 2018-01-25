import FWCore.ParameterSet.Config as cms
from  PhysicsTools.NanoAOD.common_cff import *
from RecoJets.JetProducers.AnomalousCellParameters_cfi import *
from RecoJets.JetProducers.PFJetParameters_cfi import *
from RecoBTag.SecondaryVertex.pfCombinedInclusiveSecondaryVertexV2BJetTags_cfi import *
from RecoBTag.ImpactParameter.pfImpactParameterTagInfos_cfi import pfImpactParameterTagInfos
from RecoBTag.SecondaryVertex.pfInclusiveSecondaryVertexFinderTagInfos_cfi import *
from RecoBTag.SecondaryVertex.candidateCombinedSecondaryVertexV2Computer_cfi import *
from RecoBTag.SecondaryVertex.pfBoostedDoubleSVAK8TagInfos_cfi import *

#from TrackingTools.TransientTrack.TransientTrackBuilder_cfi import *

##################### User floats producers, selectors ##########################


# Use the trivial selector to convert patMuons into reco::Muons for removal
selectedMuonsTmp = cms.EDProducer("MuonRemovalForBoostProducer", 
    src = cms.InputTag("slimmedMuons"),
    vtx = cms.InputTag("offlineSlimmedPrimaryVertices"))
selectedMuons = cms.EDFilter("CandPtrSelector", 
    src = cms.InputTag("selectedMuonsTmp"), 
    cut = cms.string("1"))

# Use the trivial selector to convert patElectrons into reco::Electrons for removal
selectedElectronsTmp = cms.EDProducer("ElectronRemovalForBoostProducer", 
    src = cms.InputTag("slimmedElectrons"),
    mvaIDMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-tight"),
    rho = cms.InputTag("fixedGridRhoFastjetAll"))
selectedElectrons = cms.EDFilter("CandPtrSelector", 
    src = cms.InputTag("selectedElectronsTmp"), 
    cut = cms.string("1"))



chsTmp1 = cms.EDFilter("CandPtrSelector", 
    src = cms.InputTag("packedPFCandidates"), 
    cut = cms.string("fromPV")
    ) 

chsTmp2 =  cms.EDProducer("CandPtrProjector", 
    src = cms.InputTag("chsTmp1"), 
    veto = cms.InputTag("selectedMuons")
    )

chs = cms.EDProducer("CandPtrProjector", 
    src = cms.InputTag("chsTmp2"), 
    veto = cms.InputTag("selectedElectrons")
    )

       

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


HTTTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
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

#Get HTTV2 fRex,Ropt...
HTTInfoTable = cms.EDProducer("SimpleHTTInfoFlatTableProducer",
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

#Get subjet btags
looseOptRHTTImpactParameterTagInfos = pfImpactParameterTagInfos.clone(
        primaryVertex = cms.InputTag("offlineSlimmedPrimaryVertices"),
        candidates = cms.InputTag("chs"),
        computeGhostTrack = cms.bool(True),
        computeProbabilities = cms.bool(True),
        maxDeltaR = cms.double(0.4),
        jets = cms.InputTag("looseOptRHTT", "SubJets")
)


looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos = pfInclusiveSecondaryVertexFinderTagInfos.clone(
                   extSVCollection = cms.InputTag('slimmedSecondaryVertices'),
                   trackIPTagInfos = cms.InputTag("looseOptRHTTImpactParameterTagInfos"),                
                )


looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags = pfCombinedInclusiveSecondaryVertexV2BJetTags.clone(
                    tagInfos = cms.VInputTag(cms.InputTag("looseOptRHTTImpactParameterTagInfos"),
                                             cms.InputTag("looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos")),
                    jetTagComputer = cms.string("candidateCombinedSecondaryVertexV2Computer")
                )


patSubJets = cms.EDProducer("PATJetProducer",
    jetSource = cms.InputTag("looseOptRHTT", "SubJets"),
    embedPFCandidates = cms.bool(False),
    addJetCorrFactors    = cms.bool(False),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("patJetCorrFactors") ),
    # btag information
    addBTagInfo          = cms.bool(True),   ## master switch
    addDiscriminators    = cms.bool(True),   ## addition btag discriminators
    discriminatorSources = cms.VInputTag(
        cms.InputTag("looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags"),
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


HTTSubjetsOrdered =  cms.EDProducer("HTTBtagMatchProducer", 
    jetSource = cms.InputTag("looseOptRHTT", "SubJets"),
    patsubjets = cms.InputTag("patSubJets")
    )

#And finally add subjets to the nanoAOD tree
HTTSubjetsBtagTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("HTTSubjetsOrdered"),
    cut = cms.string(""),
    name = cms.string("HTTV2Subjets"),
    doc  = cms.string("Btags of HTT candidate subjets"),
    singleton = cms.bool(False),
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars,
        IDPassed = Var("?pt() <= 20 || abs(eta()) >= 2.4 || neutralHadronEnergyFraction()>=0.99 || neutralEmEnergyFraction() >= 0.99 ||(chargedMultiplicity()+neutralMultiplicity()) <= 1 || chargedHadronEnergyFraction() <= 0 || chargedMultiplicity() <= 0 || chargedEmEnergyFraction() >= 0.99?0:1",float, doc="Subjet ID passed?",precision=1),
        btag  = Var("bDiscriminator('looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags')",float,doc="CMVA V2 btag discriminator",precision=10),
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
    )
)



boostedSequence = cms.Sequence(selectedMuonsTmp+selectedMuons+selectedElectronsTmp+selectedElectrons+ \
    chsTmp1+chsTmp2+chs+looseOptRHTT+looseOptRHTTImpactParameterTagInfos+ \
    looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos+ \
    looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags+patSubJets+HTTSubjetsOrdered)
boostedTables = cms.Sequence(HTTTable+HTTInfoTable+HTTSubjetsBtagTable)

