#include "Validation/Geometry/interface/MaterialBudgetCategorizer.h"

#include "G4LogicalVolumeStore.hh"
#include "G4Material.hh"
#include "G4UnitsTable.hh"
#include "G4EmCalculator.hh"
#include "G4UnitsTable.hh"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include <fstream>
#include <vector>

MaterialBudgetCategorizer::MaterialBudgetCategorizer(std::string mode,
						     std::string trackerGeometry)
{
  //----- Build map volume name - volume index
  G4LogicalVolumeStore* lvs = G4LogicalVolumeStore::GetInstance();
  G4LogicalVolumeStore::iterator ite;
  int ii = 0;
  for (ite = lvs->begin(); ite != lvs->end(); ite++) {
    theVolumeMap[(*ite)->GetName()] = ii++;
  }

  useTrackerGeometry = trackerGeometry;
  std::string theMaterialX0FileName;
  std::string theMaterialL0FileName;
  std::string thehgcalMaterialX0FileName;
  std::string thehgcalMaterialL0FileName;
  if ( mode.compare("Tracker") == 0 ) {
    if ( useTrackerGeometry == "phase1" ) {
      theMaterialX0FileName = edm::FileInPath("Validation/Geometry/data/trackerMaterials.x0").fullPath();
      buildCategoryMap(theMaterialX0FileName, theX0Map);
      theMaterialL0FileName = edm::FileInPath("Validation/Geometry/data/trackerMaterials.l0").fullPath();
      buildCategoryMap(theMaterialL0FileName, theL0Map);
    } else if ( useTrackerGeometry == "phase2" ){
      theMaterialX0FileName = edm::FileInPath("Validation/Geometry/data/RL").fullPath(); //Change file
      std::cout << "----------------------------------------------------------------------------" << std::endl;
      std::cout << "------------------------------------ X0 ------------------------------------" << std::endl;
      std::cout << "----------------------------------------------------------------------------" << std::endl;
      buildCategoryMap(theMaterialX0FileName, theX0Map);
      theMaterialL0FileName = edm::FileInPath("Validation/Geometry/data/IL").fullPath(); //Change file
      std::cout << "----------------------------------------------------------------------------" << std::endl;
      std::cout << "------------------------------------ L0 ------------------------------------" << std::endl;
      std::cout << "----------------------------------------------------------------------------" << std::endl;
      buildCategoryMap(theMaterialL0FileName, theL0Map);
    } else {
      throw cms::Exception("BadConfig") <<" (MaterialBudgetCategorizer) Unsupported geometry: " << useTrackerGeometry;
    }
  } else if ( mode.compare("HGCal") == 0 ){
      thehgcalMaterialX0FileName = edm::FileInPath("Validation/Geometry/data/hgcalMaterials.x0").fullPath();
      buildHGCalCategoryMap(thehgcalMaterialX0FileName, theHGCalX0Map);
      thehgcalMaterialL0FileName = edm::FileInPath("Validation/Geometry/data/hgcalMaterials.l0").fullPath();
      buildHGCalCategoryMap(thehgcalMaterialL0FileName, theHGCalL0Map);
  }
}

void MaterialBudgetCategorizer::buildCategoryMap(std::string theMaterialFileName, 
						 std::map<std::string,std::vector<float> >& theMap) 
{

  std::ifstream theMaterialFile(theMaterialFileName);

  if (!theMaterialFile) 
    cms::Exception("LogicError") << " File not found " << theMaterialFileName;
  
  unsigned int nCats = 0;  // number of cats is cats in file. Air and other will be added independently
  catNames.clear();
  
  int iAddedCat = 0;
  if (useTrackerGeometry == "phase1"){
    nCats = 5;
    for (auto x: {"SUP", "SEN", "CAB", "COL", "ELE"}){
      catNames.push_back(x);
      materialIDs[x] = iAddedCat;
      iAddedCat++;
    }
  } else if (useTrackerGeometry == "phase2"){
    nCats = 4;
    for (auto x: {"SUP", "SEN", "CAB", "COL_SUP"}){
      catNames.push_back(x);
      materialIDs[x] = iAddedCat;
      iAddedCat++;
    }
  } else {
    throw cms::Exception("BadConfig") <<" Unsupported geometry: " << useTrackerGeometry << "(But we should never even got here)";
  }

  catNames.push_back("OTH");
  materialIDs["OTH"] = iAddedCat; iAddedCat++;
  catNames.push_back("AIR");
  materialIDs["AIR"] = iAddedCat; iAddedCat++;

  nCategories = catNames.size();
  for (unsigned int i = 0; i < nCategories; i++){
    
  }
  
  float materialCont[nCats+2];
  for (unsigned int iCat = 0;iCat < nCats ;iCat++){
    std::cout << iCat << " "<< catNames.at(iCat) << std::endl;
    materialCont[iCat] = 0;
  }


  std::string materialName;
  float sum = 0;
  
  while(theMaterialFile) {
    theMaterialFile >> materialName;

    sum = 0;
    for (unsigned int iCat = 0; iCat < nCats; iCat++){
      theMaterialFile >> materialCont[iCat];
      sum += materialCont[iCat];
    }

    
    if (materialName[0] == '#') //Ignore comments
      continue;
 
    materialCont[nCats] = 0.00; //other
    materialCont[nCats+1] = 0.00; //air


    /// ************************** TEMP ****************************
    std::cout << "MaterialBudgetCategorizer: Material " << materialName << " filled: ";
    for (unsigned int iCat = 0; iCat < nCats; iCat++){
      std::cout << "\n\t" << catNames.at(iCat) << " " << materialCont[iCat];
    }
    std::cout << "\n\t" << catNames.at(nCats) << " " << materialCont[nCats];
    std::cout << "\n\t" << catNames.at(nCats+1) << " " << materialCont[nCats+1];
    std::cout << "\n\tSUM = " << sum <<std::endl;
    std::cout << "===============================================================" << std::endl;
    /// ***********************************************************

    
    theMap[materialName].clear();        // clear before re-filling
    for (unsigned int iCat = 0; iCat < nCats+2; iCat++){
      theMap[materialName].push_back(materialCont[iCat]); // sup
    }
    edm::LogInfo("MaterialBudget") << "MaterialBudgetCategorizer: Material " << materialName << " filled: ";
    for (unsigned int iCat = 0; iCat < nCats+2; iCat++){
      edm::LogInfo("MaterialBudget") << "\t" << catNames.at(iCat) << " " <<  materialCont[iCat];
    }
    edm::LogInfo("MaterialBudget") << "\tAdd up to: " << sum;
  }
}

void MaterialBudgetCategorizer::buildHGCalCategoryMap(std::string theMaterialFileName, 
						      std::map<std::string,std::vector<float> >& theMap)
{
  
  std::ifstream theMaterialFile(theMaterialFileName);
  if (!theMaterialFile) 
    cms::Exception("LogicError") <<" File not found " << theMaterialFileName;
  
  // fill everything as "other"
  float air,cables,copper,h_scintillator,lead,hgc_g10_fr4,silicon,stainlesssteel,wcu,oth,epoxy,kapton,aluminium; 
  air=cables=copper=h_scintillator=lead=hgc_g10_fr4=silicon=stainlesssteel=wcu=epoxy=kapton=aluminium=0.;

  std::string materialName;
  while(theMaterialFile) {
    theMaterialFile >> materialName;
    theMaterialFile >> air >> cables >> copper >> h_scintillator >> lead >> hgc_g10_fr4 >> silicon >> stainlesssteel >> wcu >> epoxy >> kapton >> aluminium;
    // Skip comments
    if (materialName[0] == '#')
      continue;
    // Substitute '*' with spaces
    std::replace(materialName.begin(), materialName.end(), '*', ' ');
    oth = 0.000;
    theMap[materialName].clear();        // clear before re-filling
    theMap[materialName].push_back(air             ); // air
    theMap[materialName].push_back(cables          ); // cables          
    theMap[materialName].push_back(copper          ); // copper          
    theMap[materialName].push_back(h_scintillator  ); // h_scintillator  
    theMap[materialName].push_back(lead            ); // lead            
    theMap[materialName].push_back(hgc_g10_fr4); // hgc_g10_fr4
    theMap[materialName].push_back(silicon         ); // silicon         
    theMap[materialName].push_back(stainlesssteel  ); // stainlesssteel
    theMap[materialName].push_back(wcu             ); // wcu
    theMap[materialName].push_back(oth             ); // oth
    theMap[materialName].push_back(epoxy             ); // epoxy
    theMap[materialName].push_back(kapton             ); // kapton
    theMap[materialName].push_back(aluminium             ); // aluminium
    edm::LogInfo("MaterialBudget") 
      << "MaterialBudgetCategorizer: material " << materialName << " filled " 
      << std::endl
      << "\tair              " << air << std::endl
      << "\tcables           " << cables << std::endl
      << "\tcopper           " << copper << std::endl
      << "\th_scintillator   " << h_scintillator << std::endl
      << "\tlead             " << lead << std::endl
      << "\thgc_g10_fr4      " << hgc_g10_fr4 << std::endl
      << "\tsilicon          " << silicon << std::endl
      << "\tstainlesssteel   " << stainlesssteel << std::endl
      << "\twcu              " << wcu << std::endl
      << "\tepoxy              " << epoxy << std::endl
      << "\tkapton            " << kapton<< std::endl
      << "\taluminium            " << aluminium<< std::endl
      << "\tOTH              " << oth;
  }

}
