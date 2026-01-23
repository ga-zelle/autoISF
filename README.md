# AutoISF version 3.2.0
This autoISF is an add-on to AAPS V3.4.0. master using oref1 and out of the box it behaves like regular AAPS. It can adapt ISF if glucose or its trends show certain behaviour. See the Quick Guide for details of those scenarios. The effects can be tuned individually to further improve your results if you already have a TIR of about 90%. Besides those adaptations there are other features like managing SMB settings or reacting to step counts. Last but not least it can serve as an enabler for Full Closed Looping (see https://discord.com/channels/953929437894803478/1025730692014936207 ).

The repo with the complete code can be found here:
https://github.com/T-o-b-i-a-s/AndroidAPS/tree/3.4.0.0+aisf3.2.0
Beware that in Android Studio you first start with its related master branch, wait for all the downloading and other updates and only finally switch to the above branch. More detailed build instructions are given in that repo including those for the new browser build option.

The main new features on the AutoISF side provided by the upgrade from 3.1.0 to 3.2.0 are:
* Display the fitted parabola in the main graph area
* Display the various AutoISF factors in the smaller graphs
* Display the effective iobTH in one of the smaller graphs
* In AAPSClient show the Script Debug from the master loop

For details of these and other minor additions see the Preface in the Quick Guide.
