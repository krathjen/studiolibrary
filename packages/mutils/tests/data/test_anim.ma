//Maya ASCII 2014 scene
//Name: test_anim.ma
//Last modified: Sat, Mar 14, 2015 04:31:24 AM
//Codeset: 1252
file -rdi 1 -ns "srcSphere" -rfn "srcSphereRN" "C:/Users/hovel/Dropbox/packages/python/Lib/site-packages/studioLibrary/site-packages/mutils/tests/data/sphere.ma";
file -rdi 1 -ns "dstSphere" -rfn "dstSphereRN" "C:/Users/hovel/Dropbox/packages/python/Lib/site-packages/studioLibrary/site-packages/mutils/tests/data/sphere.ma";
file -r -ns "srcSphere" -dr 1 -rfn "srcSphereRN" "C:/Users/hovel/Dropbox/packages/python/Lib/site-packages/studioLibrary/site-packages/mutils/tests/data/sphere.ma";
file -r -ns "dstSphere" -dr 1 -rfn "dstSphereRN" "C:/Users/hovel/Dropbox/packages/python/Lib/site-packages/studioLibrary/site-packages/mutils/tests/data/sphere.ma";
requires maya "2014";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2014";
fileInfo "version" "2014 x64";
fileInfo "cutIdentifier" "201303010241-864206";
fileInfo "osv" "Microsoft Windows 7 Ultimate Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode transform -s -n "persp";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -123.17900131274617 74.628663135067598 32.661032572240735 ;
	setAttr ".r" -type "double3" -30.338352727390017 -72.599999999996271 0 ;
createNode camera -s -n "perspShape" -p "persp";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 150.42418693917088;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 100.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 2.0350096678112575 0.39361762628711539 100.1 ;
createNode camera -s -n "frontShape" -p "front";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 61.766282942468983;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode lightLinker -s -n "lightLinker1";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
createNode displayLayer -n "defaultLayer";
createNode renderLayerManager -n "renderLayerManager";
createNode renderLayer -n "defaultRenderLayer";
	setAttr ".g" yes;
createNode script -n "sceneConfigurationScriptNode";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 24 -ast 1 -aet 48 ";
	setAttr ".st" 6;
createNode reference -n "srcSphereRN";
	setAttr -s 16 ".phl";
	setAttr ".phl[1]" 0;
	setAttr ".phl[2]" 0;
	setAttr ".phl[3]" 0;
	setAttr ".phl[4]" 0;
	setAttr ".phl[5]" 0;
	setAttr ".phl[6]" 0;
	setAttr ".phl[7]" 0;
	setAttr ".phl[8]" 0;
	setAttr ".phl[9]" 0;
	setAttr ".phl[10]" 0;
	setAttr ".phl[11]" 0;
	setAttr ".phl[12]" 0;
	setAttr ".phl[13]" 0;
	setAttr ".phl[14]" 0;
	setAttr ".phl[15]" 0;
	setAttr ".phl[16]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"srcSphereRN"
		"srcSphereRN" 0
		"srcSphereRN" 45
		1 |srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere 
		"testStatic" "testStatic" " -ci 1 -at \"double\""
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "visibility" " 1"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "translate" " -type \"double3\" 0 5 0"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "translateX" " -av"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "translateY" " -av"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "translateZ" " -av"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "rotate" " -type \"double3\" 0 0 0"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "rotateX" " -av"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "rotateY" " -av"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "rotateZ" " -av"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "scale" " -type \"double3\" 1 1 1"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"translate" " -type \"double3\" 0 8 -12"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"translateZ" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"rotate" " -type \"double3\" 45 50 90"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"rotateX" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"rotateY" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"rotateZ" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"scale" " -type \"double3\" 0.25 4.66 0.5"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"scaleX" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"scaleY" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"scaleZ" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testVector" " -k 1 -type \"double3\" 0.2 1.4 2.6"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testVector" " -k 1"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testVectorX" " -k 1"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testVectorY" " -av -k 1"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testVectorZ" " -k 1"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testColor" " -type \"float3\" 0.18 0.6 0.18"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testString" " -k 1 -type \"string\" \"Hello world\""
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testStatic" " -k 1 0"
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode.translateZ" 
		"srcSphereRN.placeHolderList[1]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.testVectorX" 
		"srcSphereRN.placeHolderList[2]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.testVectorY" 
		"srcSphereRN.placeHolderList[3]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.testVectorZ" 
		"srcSphereRN.placeHolderList[4]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.testEnum" 
		"srcSphereRN.placeHolderList[5]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.testFloat" 
		"srcSphereRN.placeHolderList[6]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.testBoolean" 
		"srcSphereRN.placeHolderList[7]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.testInteger" 
		"srcSphereRN.placeHolderList[8]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.translateY" 
		"srcSphereRN.placeHolderList[9]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.translateX" 
		"srcSphereRN.placeHolderList[10]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.translateZ" 
		"srcSphereRN.placeHolderList[11]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.rotateX" 
		"srcSphereRN.placeHolderList[12]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.rotateZ" 
		"srcSphereRN.placeHolderList[13]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.scaleX" 
		"srcSphereRN.placeHolderList[14]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.scaleZ" 
		"srcSphereRN.placeHolderList[15]" ""
		5 4 "srcSphereRN" "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere.visibility" 
		"srcSphereRN.placeHolderList[16]" "";
	setAttr ".ptag" -type "string" "";
lockNode -l 1 ;
createNode reference -n "dstSphereRN";
	setAttr ".ed" -type "dataReferenceEdits" 
		"dstSphereRN"
		"dstSphereRN" 0;
	setAttr ".ptag" -type "string" "";
lockNode -l 1 ;
createNode animCurveTU -n "srcSphere:sphere_visibility";
	setAttr ".tan" 9;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1 10 1;
	setAttr -s 2 ".kot[0:1]"  5 5;
createNode animCurveTL -n "srcSphere:sphere_translateX";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0 10 0;
createNode animCurveTL -n "srcSphere:sphere_translateY";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 8 10 8;
createNode animCurveTL -n "srcSphere:sphere_translateZ";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 -12 10 11.214436147065292;
createNode animCurveTA -n "srcSphere:sphere_rotateX";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 45 10 30.81018202226841;
createNode animCurveTA -n "srcSphere:sphere_rotateZ";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 90 10 149.70880463068096;
createNode animCurveTU -n "srcSphere:sphere_scaleX";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.25 10 0.42958527814637792;
createNode animCurveTU -n "srcSphere:sphere_scaleZ";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.5 10 0.85917055629275585;
createNode animCurveTU -n "srcSphere:sphere_testVectorX";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.2 10 0.2;
createNode animCurveTU -n "srcSphere:sphere_testVectorY";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1.4 10 1.4;
createNode animCurveTU -n "srcSphere:sphere_testVectorZ";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 2.6 10 2.6;
createNode animCurveTU -n "srcSphere:sphere_testEnum";
	setAttr ".tan" 9;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1 10 1;
	setAttr -s 2 ".kot[0:1]"  5 5;
createNode animCurveTU -n "srcSphere:sphere_testFloat";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.666 10 0.666;
createNode animCurveTU -n "srcSphere:sphere_testBoolean";
	setAttr ".tan" 9;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1 10 1;
	setAttr -s 2 ".kot[0:1]"  5 5;
createNode animCurveTU -n "srcSphere:sphere_testInteger";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 5 10 5;
createNode animCurveTL -n "dstSphere:sphere_translateY";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 8 10 8;
createNode animCurveTL -n "lockedNode_translateZ";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0 10 15;
createNode animCurveTU -n "sphere_testInteger";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 5 10 5;
createNode animCurveTU -n "sphere_testEnum";
	setAttr ".tan" 9;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1 10 1;
	setAttr -s 2 ".kot[0:1]"  5 5;
createNode animCurveTL -n "sphere_translateX";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0 10 0;
createNode animCurveTL -n "sphere_translateZ";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 -12 10 11.214436147065292;
createNode animCurveTU -n "sphere_testFloat";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.666 10 0.666;
createNode animCurveTU -n "sphere_scaleX";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.25 10 0.42958527814637792;
createNode animCurveTU -n "sphere_testVectorZ";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 2.6 10 2.6;
createNode animCurveTU -n "sphere_scaleZ";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.5 10 0.85917055629275585;
createNode animCurveTA -n "sphere_rotateX";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 45 10 30.81018202226841;
createNode animCurveTU -n "sphere_testVectorY";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1.4 10 1.4;
createNode animCurveTA -n "sphere_rotateZ";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 90 10 149.70880463068096;
createNode animCurveTU -n "sphere_visibility";
	setAttr ".tan" 9;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1 10 1;
	setAttr -s 2 ".kot[0:1]"  5 5;
createNode animCurveTU -n "sphere_testVectorX";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.2 10 0.2;
createNode animCurveTU -n "sphere_testBoolean";
	setAttr ".tan" 9;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1 10 1;
	setAttr -s 2 ".kot[0:1]"  5 5;
createNode animCurveTL -n "lockedNode_translateZ1";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0 10 15;
createNode reference -n "sharedReferenceNode";
	setAttr ".ed" -type "dataReferenceEdits" 
		"sharedReferenceNode";
select -ne :time1;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :renderPartition;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
	setAttr -s 2 ".st";
select -ne :initialShadingGroup;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
	setAttr -s 2 ".dsm";
	setAttr -k on ".mwc";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
	setAttr -k on ".mwc";
	setAttr ".ro" yes;
select -ne :defaultShaderList1;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
	setAttr -s 2 ".s";
select -ne :postProcessList1;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
	setAttr -s 6 ".r";
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
select -ne :defaultRenderGlobals;
	setAttr ".ep" 1;
select -ne :defaultResolution;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
	setAttr -av ".w" 640;
	setAttr -av ".h" 480;
	setAttr -k on ".pa" 1;
	setAttr -k on ".al";
	setAttr -av ".dar" 1.3333332538604736;
	setAttr -k on ".ldar";
	setAttr -k on ".off";
	setAttr -k on ".fld";
	setAttr -k on ".zsl";
select -ne :defaultLightSet;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
	setAttr -k on ".mwc";
	setAttr ".ro" yes;
select -ne :hardwareRenderGlobals;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 18 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surfaces" "Particles" "Fluids" "Image Planes" "UI:" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 18 0 1 1 1 1 1
		 1 0 0 0 0 0 0 0 0 0 0 0 ;
select -ne :defaultHardwareRenderGlobals;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
	setAttr ".fn" -type "string" "im";
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
select -ne :ikSystem;
	setAttr -s 4 ".sol";
connectAttr "lockedNode_translateZ.o" "srcSphereRN.phl[1]";
connectAttr "srcSphere:sphere_testVectorX.o" "srcSphereRN.phl[2]";
connectAttr "srcSphere:sphere_testVectorY.o" "srcSphereRN.phl[3]";
connectAttr "srcSphere:sphere_testVectorZ.o" "srcSphereRN.phl[4]";
connectAttr "srcSphere:sphere_testEnum.o" "srcSphereRN.phl[5]";
connectAttr "srcSphere:sphere_testFloat.o" "srcSphereRN.phl[6]";
connectAttr "srcSphere:sphere_testBoolean.o" "srcSphereRN.phl[7]";
connectAttr "srcSphere:sphere_testInteger.o" "srcSphereRN.phl[8]";
connectAttr "srcSphere:sphere_translateY.o" "srcSphereRN.phl[9]";
connectAttr "srcSphere:sphere_translateX.o" "srcSphereRN.phl[10]";
connectAttr "srcSphere:sphere_translateZ.o" "srcSphereRN.phl[11]";
connectAttr "srcSphere:sphere_rotateX.o" "srcSphereRN.phl[12]";
connectAttr "srcSphere:sphere_rotateZ.o" "srcSphereRN.phl[13]";
connectAttr "srcSphere:sphere_scaleX.o" "srcSphereRN.phl[14]";
connectAttr "srcSphere:sphere_scaleZ.o" "srcSphereRN.phl[15]";
connectAttr "srcSphere:sphere_visibility.o" "srcSphereRN.phl[16]";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "sharedReferenceNode.sr" "dstSphereRN.sr";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of test_anim.ma
