**DO NOT USE IT WITH LIBRE CGMs**

Files for AAPS version 2.8.1.1

Here, only those files are included that need to be replaced in the original release

Changes since version 2.7.1
1. autoISF uses its own variables autoisf_max and autoisf_hourlychange and no longer the Autosense parameters.
   This means the effects of the two methods are now completely independant
2. These new variables are maintained by the user in a menu
3. For the emulator you no longer need to copy logfiles to the working folder. Instead you can just refer
to them whereever they are stored on the PC. This means you may just keep all your logfiles in a single location
and without having copies sitting around in various places.
4. The variant definition files for the emulator called ".dat" should now be called ".vdf" instead.
   For downward compatibility the previous naming is still supported but discouraged.
