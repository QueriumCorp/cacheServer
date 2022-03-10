(* ****************************************************************************
(c) Copyright 2020 Querium Corp. All rights reserved.
This computer program contains Confidential, Proprietary information and is a
Trade Secret of Querium Corp. This document is covered under a Non-Disclosure
Agreement. All use, disclosure, and/or reproduction is prohibited unless
authorized in writing. Copying this software in violation of Federal Copyright
Law is a criminal offense. Deciphering or decompiling the computer program, or
developing or deriving the source code of the computer program, is prohibited.
This computer program may also be protected under laws of non-U.S. countries,
including copyright and trade secret laws.
**************************************************************************** *)

(*******************************************************************************
runCaching.wl is expected to run from cacheServer.py.
The following design document describes the generating image in the caching
process:
https://docs.google.com/document/d/1Pe4SdHZVSr9Tpgg20RIif1SNmAaDdlfeEazZNaeltDw/edit?usp=sharing

IMPORTANT:
The current working directory still needs to be set to "/path/to/CommonCore"
when the caching image is used. Otherwise, getGitHash[] will not work!

runCaching.wl expects a string of JSON as an argument and the following fields:
'{
  "dirCommonCore": "/path/to/CommonCore",
  "loadFromImgOn": true,
  "img": "/path/to/cacheImg.mx",
  "id": "",
  "mma_id": "",
  "gradeStyle": "",
  "policies": "",
  "limitStepTime": "",
  "limitSteps": "",
  "limitMmaTime": "",
  "cachingOrder": "",
  "hintL": "",
  "showMeL": "",
  "stepCount": "",
  "stepsCompleted": "",
  "timeCompleted": "",
  "gitHash": "",
  "gitRedis": "",
  "timeOutTime": "",
  "ruleMatchTimeOutTime": "",
  "clearOldCacheQ": "",
  "modQidType": ""
 }'

* NOTE:
* Run the script on an ai server:
  /path/to/WolframScript -script runCaching.wl  '{"aField": "aValue"}'

* Run the script on Evan's mac:
  /Applications/Mathematica.app/Contents/MacOS/WolframScript -script /Users/evan/Documents/work/querium/coding/mma/CommonCore/cronjob/cacheServer/runCaching.wl '{"dirCommonCore": "/tmp/stepwise/28746af9688a13aca6084ba8a1833b9f5a682601/CommonCore", "img": "/tmp/stepwise/28746af9688a13aca6084ba8a1833b9f5a682601/images/cacheImg.mx", "loadFromImgOn": true}'
*******************************************************************************)
(*** Support ***)
fixPolicy[policy_]:= "$A1$";

fixPolicy[policy_String]:= Module[
  {cleaned, rslt},
  cleaned = StringTrim[StringReplace[policy, "$" -> ""]];
  If[cleaned==="", Return["$A1$"]];

  StringJoin[{"$", cleaned, "$"}]
];

(*** MAIN ***)
Print[$ProcessID, " - - - - - - - - - - - - - - - - - - - - - - - - - "];
Print[$ProcessID, " START: caching: ", DateString[]];
(*Print["Print[$CommandLine]: ", $ScriptCommandLine];*)

(*** Read JSON argument ***)
$confCacheMma = ImportString[$ScriptCommandLine[[2]], "RawJSON"];
If[Head[$confCacheMma]=!=Association,
  Exit[6];
];
(* Scan[Print[#, ": ", $confCacheMma[#]]&, Keys[$confCacheMma]]; *)

(*** Fix the policy string ***)
$confCacheMma["policies"] = fixPolicy[$confCacheMma["policies"]];

(*** Verify the directories exist ***)
If[!DirectoryQ[$confCacheMma["dirCommonCore"]],
  Print[$ProcessID, " Invalid path to dirCommonCore"];
  Exit[4];
];

(*** If StepWise is loaded from an image, make sure it exists ***)
If[$confCacheMma["loadFromImgOn"] && !FileExistsQ[$confCacheMma["img"]],
  Print[$ProcessID, " Missing the cache image: ", $confCacheMma["img"]];
  Exit[5];
];

(*** Load Stepwise ***)
SetDirectory[$confCacheMma["dirCommonCore"]];
If[TrueQ[$confCacheMma["loadFromImgOn"]],
  Print[$ProcessID, " Loading StepWise from an image ....."];
  Get[$confCacheMma["img"]];
  Print[$ProcessID, " Overloading Mma functions ....."];
  Unprotect[Simplify];
  Simplify[expr_?StepWise`complexExprQ] := Simplify[expr /. {Users`i -> System`I}];
  Protect[Simplify];

  Unprotect[Factor];
  Factor[expr_, meth_]:= Factor[expr];
  Protect[Factor];

  Unprotect[Simplify];
  Simplify[(form:StepWise`$anyInequality)[x_Symbol, r_Rational]] := form[x,r];
  Protect[Simplify];

  ,
  Print[$ProcessID, " Loading StepWise without an image ....."];
  << StepWise.m;
];

(*** Configure cache settings ***)
StepWise`$cachingOn = $confCacheMma["cachingOn"];
StepWise`$jsonResponse = $confCacheMma["jsonResponse"];
StepWise`$redisOn = $confCacheMma["redisOn"];
StepWise`$saveStateInStateOn = $confCacheMma["saveStateInStateOn"];
StepWise`$autoCachingOn = $confCacheMma["autoCachingOn"];

(*** Update cache_mma ***)
Get[FileNameJoin[{$confCacheMma["dirCommonCore"], "include", "mysqlConn.m"}]];
dbStatus = StepWise`updateCache[$confCacheMma["id"],
  {"pid", "status", "started"},
  {$ProcessID, "running", DateString["ISODateTime"]}
];
If[dbStatus =!= 1,
  Print[$ProcessID, " Unable to update cache_mma with pid, status, started"];
  Exit[7];
];
Print[$ProcessID, " Updated cache_mma table"];

(*** Run caching ***)
cacheRslt = StepWise`cacheLatexPath[$confCacheMma];
Print[$ProcessID, " CACHE RESULT"];
Scan[Print[$ProcessID, " ", #, ": ", cacheRslt[#]]&, Keys[cacheRslt]];

(*** Update cache_mma the result ***)
cacheRslt["finished"] = DateString["ISODateTime"];
dbStatus = StepWise`updateCacheTbl[$confCacheMma, cacheRslt];
If[dbStatus =!= 1,
  Print[$ProcessID, " Unable to update cache_mma with result"];
  Exit[7];
];

Print[$ProcessID, " END: caching: ", DateString[]];
Exit[];