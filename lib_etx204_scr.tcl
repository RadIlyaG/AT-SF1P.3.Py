lappend auto_path C:/Tcl/lib/tcl8.6 
lappend auto_path C:/Tcl/lib 
lappend auto_path c:/tcl/lib/teapot/package/win32-ix86/lib 
lappend auto_path c:/tcl/lib/teapot/package/tcl/lib 
lappend auto_path C:/Tcl/lib/tcl8.6/tcllib1.15 
lappend auto_path C:/Tcl/lib/tk8.6 
lappend auto_path C:/Tcl/lib/tk8.6/ttk


package require RLEH  
package require RLEtxGen
catch {RLEH::Open}
wm withdraw .
#console show

# set gaSet(comGen1) 5
# proc OpenEtxGen {} {
  # global gaSet gaEtx204Conf
  # foreach gen {1} {   
    # set com $gaSet(comGen$gen)
    # puts "Open com:$com"
    # set gaSet(idGen$gen) [RLEtxGen::Open $com -package RLCom] 
    # if {[string is integer $gaSet(idGen$gen)] && $gaSet(idGen$gen)>0 } {   
      # set ret 0
    # } else {
      # set gaSet(fail) "Open Generator-$gen fail"
      # set ret -1
      # break
    # }  
  # }
  # return $ret 
# }


# proc SetPio {pio type usbCh status} {
  # #***************************************************************************
  # #** SetPio
  # #***************************************************************************
  # #puts "$pio $type $usbCh $status"
  # set id [RLUsbPio::Open $pio $type $usbCh]
  # RLUsbPio::Set $id $status
  # RLUsbPio::Close $id
# }


# proc GetPio {id} {
  # #***************************************************************************
  # #** GetPio
  # #***************************************************************************
  # #puts "$id"
  # set res [RLUsbPio::Get $id buffer]
  # if {$res==0} {
    # return "$buffer"
  # } else {
    # return -1
  # } 
# }




# proc RetriveUsbChannel {sn} {
  # #***************************************************************************
  # #** RetriveUsbChannel
  # #***************************************************************************
  # set boxL ""
  # set boxL [array names ::RLUsbPio::description]
  # set snList [lsort -unique [regexp -all -inline "(\\d,SerialNumber)" $boxL]]
  # if {[llength $snList]==0} {
    # return -1
  # }
  # if {[llength $snList]==1} {
    # return 1
  # }
  # puts $snList
  # foreach i $snList {
    # puts $RLUsbPio::description($i)
    # if {$RLUsbPio::description($i)==$sn} {
      # return [lindex [split $i ,] 0]
    # }
  # }
  # return -2
# }

