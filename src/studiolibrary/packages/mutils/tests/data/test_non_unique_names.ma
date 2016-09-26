//Maya ASCII 2013 scene
//Name: test_non_unique_names.ma
//Last modified: Wed, Aug 20, 2014 02:43:51 PM
//Codeset: UTF-8
file -rdi 1 -ns "srcSphere" -rfn "srcSphereRN" "C:/Users/hovel/Dropbox/packages/python/Lib/site-packages/studioLibrary/site-packages/mutils/tests/data/sphere.ma";
file -r -ns "srcSphere" -dr 1 -rfn "srcSphereRN" "C:/Users/hovel/Dropbox/packages/python/Lib/site-packages/studioLibrary/site-packages/mutils/tests/data/sphere.ma";
requires maya "2013";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2013";
fileInfo "version" "2013 Service Pack 2P12 x64";
fileInfo "cutIdentifier" "201304120319-868747";
fileInfo "osv" "Linux 3.5.4-2.10-desktop #1 SMP PREEMPT Fri Oct 5 14:56:49 CEST 2012 x86_64";
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
createNode transform -n "group";
	addAttr -ci true -sn "testMessage" -ln "testMessage" -at "message";
createNode transform -n "offset" -p "group";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode transform -n "lockedNode" -p "|group|offset";
createNode transform -n "sphere" -p "|group|offset|lockedNode";
	addAttr -ci true -sn "testVector" -ln "testVector" -at "double3" -nc 3;
	addAttr -ci true -sn "testVectorX" -ln "testVectorX" -at "double" -p "testVector";
	addAttr -ci true -sn "testVectorY" -ln "testVectorY" -at "double" -p "testVector";
	addAttr -ci true -sn "testVectorZ" -ln "testVectorZ" -at "double" -p "testVector";
	addAttr -ci true -uac -sn "testColor" -ln "testColor" -at "float3" -nc 3;
	addAttr -ci true -sn "testRed" -ln "testRed" -at "float" -p "testColor";
	addAttr -ci true -sn "testGreen" -ln "testGreen" -at "float" -p "testColor";
	addAttr -ci true -sn "testRed" -ln "testRed" -at "float" -p "testColor";
	addAttr -ci true -sn "testString" -ln "testString" -dt "string";
	addAttr -ci true -sn "testEnum" -ln "testEnum" -min 0 -max 2 -en "Apple:Lemon:Banana" 
		-at "enum";
	addAttr -ci true -sn "testFloat" -ln "testFloat" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "testBoolean" -ln "testBoolean" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "testInteger" -ln "testInteger" -min 0 -max 10 -at "long";
	addAttr -ci true -sn "testLocked" -ln "testLocked" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "testHidden" -ln "testHidden" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "testConnect" -ln "testConnect" -at "double";
	addAttr -ci true -sn "testAnimated" -ln "testAnimated" -at "double";
	addAttr -ci true -sn "testMessage" -ln "testMessage" -at "message";
	setAttr -k on ".testVector";
	setAttr -k on ".testVectorX";
	setAttr -k on ".testVectorY";
	setAttr -k on ".testVectorZ";
	setAttr -k on ".testString";
	setAttr -k on ".testEnum" 2;
	setAttr -k on ".testFloat";
	setAttr -k on ".testBoolean";
	setAttr -k on ".testInteger";
	setAttr -l on -k on ".testLocked";
	setAttr -k on ".testConnect";
	setAttr -k on ".testAnimated";
createNode mesh -n "sphereShape" -p "|group|offset|lockedNode|sphere";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".vnm" 0;
createNode transform -n "group1";
	addAttr -ci true -sn "testMessage" -ln "testMessage" -at "message";
createNode transform -n "offset" -p "group1";
	setAttr -l on ".v";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode transform -n "lockedNode" -p "|group1|offset";
createNode transform -n "sphere" -p "|group1|offset|lockedNode";
	addAttr -ci true -sn "testVector" -ln "testVector" -at "double3" -nc 3;
	addAttr -ci true -sn "testVectorX" -ln "testVectorX" -at "double" -p "testVector";
	addAttr -ci true -sn "testVectorY" -ln "testVectorY" -at "double" -p "testVector";
	addAttr -ci true -sn "testVectorZ" -ln "testVectorZ" -at "double" -p "testVector";
	addAttr -ci true -uac -sn "testColor" -ln "testColor" -at "float3" -nc 3;
	addAttr -ci true -sn "testRed" -ln "testRed" -at "float" -p "testColor";
	addAttr -ci true -sn "testGreen" -ln "testGreen" -at "float" -p "testColor";
	addAttr -ci true -sn "testRed" -ln "testRed" -at "float" -p "testColor";
	addAttr -ci true -sn "testString" -ln "testString" -dt "string";
	addAttr -ci true -sn "testEnum" -ln "testEnum" -min 0 -max 2 -en "Apple:Lemon:Banana" 
		-at "enum";
	addAttr -ci true -sn "testFloat" -ln "testFloat" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "testBoolean" -ln "testBoolean" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "testInteger" -ln "testInteger" -min 0 -max 10 -at "long";
	addAttr -ci true -sn "testLocked" -ln "testLocked" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "testHidden" -ln "testHidden" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "testConnect" -ln "testConnect" -at "double";
	addAttr -ci true -sn "testAnimated" -ln "testAnimated" -at "double";
	addAttr -ci true -sn "testMessage" -ln "testMessage" -at "message";
	setAttr -k on ".testVector";
	setAttr -k on ".testVectorX";
	setAttr -k on ".testVectorY";
	setAttr -k on ".testVectorZ";
	setAttr -k on ".testString";
	setAttr -k on ".testEnum" 2;
	setAttr -k on ".testFloat";
	setAttr -k on ".testBoolean";
	setAttr -k on ".testInteger";
	setAttr -l on -k on ".testLocked";
	setAttr -k on ".testConnect";
	setAttr -k on ".testAnimated";
createNode mesh -n "sphereShape" -p "|group1|offset|lockedNode|sphere";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".vnm" 0;
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
		"srcSphereRN" 43
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
createNode renderLayerManager -n "dstSphere:renderLayerManager";
createNode renderLayer -n "dstSphere:defaultRenderLayer";
	setAttr ".g" yes;
createNode animCurveTU -n "sphere_testAnimated";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0 10 10;
createNode polySphere -n "srcPolySphere";
	setAttr ".r" 4.1417806816985845;
createNode animCurveTU -n "sphere_testAnimated1";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0 10 10;
createNode polySphere -n "srcPolySphere1";
	setAttr ".r" 4.1417806816985845;
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".o" 1;
	setAttr -k on ".unw" 1;
	setAttr -k on ".etw";
	setAttr -k on ".tps";
	setAttr -k on ".tms";
lockNode -l 1 ;
select -ne :renderPartition;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".st";
	setAttr -cb on ".an";
	setAttr -cb on ".pt";
lockNode -l 1 ;
select -ne :initialShadingGroup;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 3 ".dsm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
lockNode -l 1 ;
select -ne :initialParticleSE;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
select -ne :defaultShaderList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".s";
select -ne :postProcessList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
	setAttr -s 6 ".r";
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultResolution;
	setAttr -k on ".cch";
	setAttr -k on ".nds";
	setAttr -av ".w";
	setAttr -av ".h";
	setAttr -k on ".pa" 1;
	setAttr -k on ".al";
	setAttr -av ".dar";
	setAttr -k on ".ldar";
	setAttr -k on ".off";
	setAttr -k on ".fld";
	setAttr -k on ".zsl";
select -ne :defaultLightSet;
	setAttr -k on ".cch";
	setAttr -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -k on ".mwc";
	setAttr -k on ".an";
	setAttr -k on ".il";
	setAttr -k on ".vo";
	setAttr -k on ".eo";
	setAttr -k on ".fo";
	setAttr -k on ".epo";
	setAttr -k on ".ro" yes;
select -ne :defaultObjectSet;
	setAttr ".ro" yes;
lockNode -l 1 ;
select -ne :hardwareRenderGlobals;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
	setAttr -k off ".fbfm";
	setAttr -k off -cb on ".ehql";
	setAttr -k off -cb on ".eams";
	setAttr -k off -cb on ".eeaa";
	setAttr -k off -cb on ".engm";
	setAttr -k off -cb on ".mes";
	setAttr -k off -cb on ".emb";
	setAttr -av -k off -cb on ".mbbf";
	setAttr -k off -cb on ".mbs";
	setAttr -k off -cb on ".trm";
	setAttr -k off -cb on ".tshc";
	setAttr -k off ".enpt";
	setAttr -k off -cb on ".clmt";
	setAttr -k off -cb on ".tcov";
	setAttr -k off -cb on ".lith";
	setAttr -k off -cb on ".sobc";
	setAttr -k off -cb on ".cuth";
	setAttr -k off -cb on ".hgcd";
	setAttr -k off -cb on ".hgci";
	setAttr -k off -cb on ".mgcs";
	setAttr -k off -cb on ".twa";
	setAttr -k off -cb on ".twz";
	setAttr -k on ".hwcc";
	setAttr -k on ".hwdp";
	setAttr -k on ".hwql";
	setAttr -k on ".hwfr";
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 18 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surfaces" "Particles" "Fluids" "Image Planes" "UI:" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 18 0 1 1 1 1 1
		 1 0 0 0 0 0 0 0 0 0 0 0 ;
select -ne :defaultHardwareRenderGlobals;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -av -k on ".rp";
	setAttr -k on ".cai";
	setAttr -k on ".coi";
	setAttr -cb on ".bc";
	setAttr -av -k on ".bcb";
	setAttr -av -k on ".bcg";
	setAttr -av -k on ".bcr";
	setAttr -k on ".ei";
	setAttr -k on ".ex";
	setAttr -av -k on ".es";
	setAttr -av -k on ".ef";
	setAttr -av -k on ".bf";
	setAttr -k on ".fii";
	setAttr -av -k on ".sf";
	setAttr -k on ".gr";
	setAttr -k on ".li";
	setAttr -k on ".ls";
	setAttr -k on ".mb";
	setAttr -k on ".ti";
	setAttr -k on ".txt";
	setAttr -k on ".mpr";
	setAttr -k on ".wzd";
	setAttr ".fn" -type "string" "im";
	setAttr -k on ".if";
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
	setAttr -k on ".as";
	setAttr -k on ".ds";
	setAttr -k on ".lm";
	setAttr -k on ".fir";
	setAttr -k on ".aap";
	setAttr -k on ".gh";
	setAttr -cb on ".sd";
lockNode -l 1 ;
select -ne :ikSystem;
	setAttr -k on ".cch";
	setAttr -k on ".ihi";
	setAttr -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -av ".gsn";
	setAttr -k on ".gsv";
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
connectAttr "|group|offset|lockedNode|sphere.msg" "group.testMessage" -l on;
connectAttr "|group|offset|lockedNode|sphere.ty" "|group|offset|lockedNode|sphere.testConnect"
		;
connectAttr "sphere_testAnimated.o" "|group|offset|lockedNode|sphere.testAnimated"
		;
connectAttr "group.msg" "|group|offset|lockedNode|sphere.testMessage" -l on;
connectAttr "srcPolySphere.out" "|group|offset|lockedNode|sphere|sphereShape.i";
connectAttr "|group1|offset|lockedNode|sphere.msg" "group1.testMessage" -l on;
connectAttr "|group1|offset|lockedNode|sphere.ty" "|group1|offset|lockedNode|sphere.testConnect"
		;
connectAttr "sphere_testAnimated1.o" "|group1|offset|lockedNode|sphere.testAnimated"
		;
connectAttr "group1.msg" "|group1|offset|lockedNode|sphere.testMessage" -l on;
connectAttr "srcPolySphere1.out" "|group1|offset|lockedNode|sphere|sphereShape.i"
		;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "dstSphere:renderLayerManager.rlmi[0]" "dstSphere:defaultRenderLayer.rlid"
		;
connectAttr "|group|offset|lockedNode|sphere|sphereShape.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|group1|offset|lockedNode|sphere|sphereShape.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "dstSphere:defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "dstSphere:defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "dstSphere:defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of test_non_unique_names.ma
