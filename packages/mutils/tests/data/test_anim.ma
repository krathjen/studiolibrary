//Maya ASCII 2018 scene
//Name: test_anim.ma
//Last modified: Fri, Aug 17, 2018 11:43:12 AM
//Codeset: 1252
file -rdi 1 -ns "srcSphere" -rfn "srcSphereRN" -typ "mayaAscii" "sphere.ma";
file -rdi 1 -ns "dstSphere" -rfn "dstSphereRN" -typ "mayaAscii" "sphere.ma";
file -r -ns "srcSphere" -dr 1 -rfn "srcSphereRN" -typ "mayaAscii" "sphere.ma";
file -r -ns "dstSphere" -dr 1 -rfn "dstSphereRN" -typ "mayaAscii" "sphere.ma";
requires maya "2018";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2018";
fileInfo "version" "2018";
fileInfo "cutIdentifier" "201706261615-f9658c4cfc";
fileInfo "osv" "Microsoft Windows 8 Business Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "1DB42BED-462B-3B26-0CCE-04ACF5EB4807";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -123.17900131274617 74.628663135067598 32.661032572240735 ;
	setAttr ".r" -type "double3" -30.338352727390017 -72.599999999996271 0 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "C6DA7E1B-42D6-DAD6-C434-3FBA9BF5C29F";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 150.42418693917088;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "0C8531AE-4DB6-8234-0EEC-8898DB568CC3";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 100.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "7C9A6610-4C33-FB0C-D2CE-3E8D90DBCD7E";
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
	rename -uid "E0C97759-4C02-050B-5C82-5B8E69ADBF20";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 2.0350096678112575 0.39361762628711539 100.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "01FB05CA-471A-EFC3-3C4B-4E8F734318FA";
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
	rename -uid "9902481E-4F28-F4A5-77B0-84A0BB6B4C7E";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "6FEAC61C-467E-28BB-87DC-EC86E914157E";
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
	rename -uid "683B78EF-4083-8D4E-3D68-70A1DB8799D8";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
	rename -uid "5437473B-4B79-C865-8061-57BCBF9D6EAB";
createNode displayLayer -n "defaultLayer";
	rename -uid "51738772-4842-9807-96DB-C8B837221923";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "3359F2F5-47FD-9064-F18D-888178149A11";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "4C4B9365-4BF4-3F4F-7950-AA977C9A9FCF";
	setAttr ".g" yes;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "1E996B38-46B9-8824-929B-64A5AD1AA52F";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 24 -ast 1 -aet 48 ";
	setAttr ".st" 6;
createNode reference -n "srcSphereRN";
	rename -uid "3DA78D3C-4AC5-86BE-AE2F-F3B14F606A39";
	setAttr ".fn[0]" -type "string" "C:/Users/Hovel/Dropbox/dev/studiolibrary/packages/mutils/tests/data/sphere.ma";
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
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "translate" " -type \"double3\" 0 5 15"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "translateX" " -av"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "translateY" " -av"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "translateZ" " -av"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "rotate" " -type \"double3\" 0 0 0"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "rotateX" " -av"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "rotateY" " -av"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "rotateZ" " -av"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode" "scale" " -type \"double3\" 1 1 1"
		
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"translate" " -type \"double3\" 0 8 11.21443614706529246"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"translateZ" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"rotate" " -type \"double3\" 30.81018202226841041 50 149.70880463068095878"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"rotateX" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"rotateY" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"rotateZ" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"scale" " -type \"double3\" 0.42958527814637792 4.66 0.85917055629275585"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"scaleX" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"scaleY" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"scaleZ" " -av"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testVector" " -k 1 -type \"double3\" 0.2 2 2.6"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testVector" " -k 1"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testVectorX" " -k 1"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testVectorY" " -av -k 1"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testVectorZ" " -k 1"
		2 "|srcSphere:group|srcSphere:offset|srcSphere:lockedNode|srcSphere:sphere" 
		"testColor" " -type \"float3\" 0.18000000999999999 0.60000001999999997 0.18000000999999999"
		
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
	rename -uid "AFE2D9D7-46E5-91AB-6626-9781ED31AD43";
	setAttr ".fn[0]" -type "string" "C:/Users/Hovel/Dropbox/dev/studiolibrary/packages/mutils/tests/data/sphere.ma{1}";
	setAttr ".ed" -type "dataReferenceEdits" 
		"dstSphereRN"
		"dstSphereRN" 0;
	setAttr ".ptag" -type "string" "";
lockNode -l 1 ;
createNode animCurveTU -n "srcSphere:sphere_visibility";
	rename -uid "432F0F5A-4B9D-4D58-39A3-FCBDF6497BDF";
	setAttr ".tan" 9;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1 10 1;
	setAttr -s 2 ".kot[0:1]"  5 5;
createNode animCurveTL -n "srcSphere:sphere_translateX";
	rename -uid "1EA6AA65-4159-6C8D-6043-D196D4C1FA6E";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0 10 0;
createNode animCurveTL -n "srcSphere:sphere_translateY";
	rename -uid "338429DD-4684-C95C-2FDC-979AA69645E1";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 8 10 8;
createNode animCurveTL -n "srcSphere:sphere_translateZ";
	rename -uid "E91B78A7-49D3-A8A2-2813-638F68417707";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 -12 10 11.214436147065292;
createNode animCurveTA -n "srcSphere:sphere_rotateX";
	rename -uid "EC93C735-4573-2AE3-2969-99A57C5ACAE3";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 45 10 30.81018202226841;
createNode animCurveTA -n "srcSphere:sphere_rotateZ";
	rename -uid "9748978E-4850-5887-2CFC-0EBABFD2EA6F";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 90 10 149.70880463068096;
createNode animCurveTU -n "srcSphere:sphere_scaleX";
	rename -uid "DA6763FC-48D7-2A42-FF55-B98B7A656915";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.25 10 0.42958527814637792;
createNode animCurveTU -n "srcSphere:sphere_scaleZ";
	rename -uid "435F01E2-4BD6-A0FD-DFD1-BC82A9F029CA";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.5 10 0.85917055629275585;
createNode animCurveTU -n "srcSphere:sphere_testVectorX";
	rename -uid "16E64E43-43AB-33F3-F0AC-39BAB399A0D7";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.2 10 0.2;
createNode animCurveTU -n "srcSphere:sphere_testVectorY";
	rename -uid "DAA22FC0-4C5A-30B4-FB7A-CFB0DF1BCF38";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1.4 10 2;
createNode animCurveTU -n "srcSphere:sphere_testVectorZ";
	rename -uid "30F7F820-49F2-2894-F656-3285EDCE7072";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 2.6 10 2.6;
createNode animCurveTU -n "srcSphere:sphere_testEnum";
	rename -uid "2FFD133D-4A06-09A3-B502-608D0A4C633C";
	setAttr ".tan" 9;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1 10 1;
	setAttr -s 2 ".kot[0:1]"  5 5;
createNode animCurveTU -n "srcSphere:sphere_testFloat";
	rename -uid "4042C3F3-42CD-EB3C-BB58-3EA3027D81B6";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.666 10 0.666;
createNode animCurveTU -n "srcSphere:sphere_testBoolean";
	rename -uid "87E936B8-429A-A60A-ADFA-5F95AAAC6468";
	setAttr ".tan" 9;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1 10 1;
	setAttr -s 2 ".kot[0:1]"  5 5;
createNode animCurveTU -n "srcSphere:sphere_testInteger";
	rename -uid "0887AA23-423A-CBA0-2B30-E2AC5918B17F";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 5 10 5;
createNode animCurveTL -n "dstSphere:sphere_translateY";
	rename -uid "E50C488D-4323-1DC6-79E7-70B0708D04BA";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 8 10 8;
createNode animCurveTL -n "lockedNode_translateZ";
	rename -uid "0DC65A76-484E-6462-E860-F3BCF2DB11E8";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0 10 15;
createNode animCurveTU -n "sphere_testInteger";
	rename -uid "4FF2C0E2-45B6-B4AA-FB41-4ABB2EE5361A";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 5 10 5;
createNode animCurveTU -n "sphere_testEnum";
	rename -uid "7A7F207F-4DAF-A2E3-5EB7-F28D0937FBFA";
	setAttr ".tan" 9;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1 10 1;
	setAttr -s 2 ".kot[0:1]"  5 5;
createNode animCurveTL -n "sphere_translateX";
	rename -uid "4530CAC3-4D36-2030-7432-7E982AB10769";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0 10 0;
createNode animCurveTL -n "sphere_translateZ";
	rename -uid "8E5FEB5F-4AB5-C878-AE72-3BBAEE1B5690";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 -12 10 11.214436147065292;
createNode animCurveTU -n "sphere_testFloat";
	rename -uid "AD47B139-4F53-730D-6965-7F8DC1BAD910";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.666 10 0.666;
createNode animCurveTU -n "sphere_scaleX";
	rename -uid "16333D29-4B5C-E912-D6CF-9D886EE319F5";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.25 10 0.42958527814637792;
createNode animCurveTU -n "sphere_testVectorZ";
	rename -uid "E16036AD-4240-CB68-F106-408B16477DF3";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 2.6 10 2.6;
createNode animCurveTU -n "sphere_scaleZ";
	rename -uid "87119A71-47C7-3873-1969-CFBED2917B93";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.5 10 0.85917055629275585;
createNode animCurveTA -n "sphere_rotateX";
	rename -uid "317683D0-433D-1160-AE9A-0BAEF1C05ACE";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 45 10 30.81018202226841;
createNode animCurveTU -n "sphere_testVectorY";
	rename -uid "22763755-4C6F-1640-2BAD-82B7756AACC9";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1.4 10 1.4;
createNode animCurveTA -n "sphere_rotateZ";
	rename -uid "4494DBB7-4ACD-90EA-4591-9B8F4147F8F4";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 90 10 149.70880463068096;
createNode animCurveTU -n "sphere_visibility";
	rename -uid "DC2B2CF0-4EE5-9C52-E3DF-7F810C7F539E";
	setAttr ".tan" 9;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1 10 1;
	setAttr -s 2 ".kot[0:1]"  5 5;
createNode animCurveTU -n "sphere_testVectorX";
	rename -uid "A1014D06-465F-2C98-84D6-37A9748D84F6";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0.2 10 0.2;
createNode animCurveTU -n "sphere_testBoolean";
	rename -uid "923BD86B-4028-CE24-9571-D7AEFBA37F9D";
	setAttr ".tan" 9;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 1 10 1;
	setAttr -s 2 ".kot[0:1]"  5 5;
createNode animCurveTL -n "lockedNode_translateZ1";
	rename -uid "0EDD0EA5-4B3F-720B-7098-30BFDEC1D4CC";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  1 0 10 15;
createNode reference -n "sharedReferenceNode";
	rename -uid "7D88D4B9-48AB-CA73-4C5A-809CA468A9CB";
	setAttr ".ed" -type "dataReferenceEdits" 
		"sharedReferenceNode";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "61C17C93-4277-E4C3-47CB-409294CA1315";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "60911DE3-450F-4BEC-77C1-1D90046A72C2";
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".o" 10;
	setAttr -k on ".unw" 10;
	setAttr -k on ".etw";
	setAttr -k on ".tps";
	setAttr -k on ".tms";
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 18 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surfaces" "Particles" "Fluids" "Image Planes" "UI:" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 18 0 1 1 1 1 1
		 1 0 0 0 0 0 0 0 0 0 0 0 ;
	setAttr ".etmr" no;
	setAttr ".tmr" 4096;
select -ne :renderPartition;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".st";
	setAttr -cb on ".an";
	setAttr -cb on ".pt";
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultShaderList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
	setAttr -s 3 ".r";
select -ne :initialShadingGroup;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 4 ".dsm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
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
select -ne :defaultColorMgtGlobals;
	setAttr ".cme" no;
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
connectAttr "sharedReferenceNode.sr" "srcSphereRN.sr";
connectAttr "sharedReferenceNode.sr" "dstSphereRN.sr";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of test_anim.ma
