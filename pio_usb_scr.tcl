package require RLEH
package require RLUsbPio
console show

catch {RLEH::Close}
RLEH::Open

if {[lindex $argv 0]=="RetriveUsbChannel"} {
  set res [array get ::RLUsbPio::description]
} else {
  set channel [lindex $argv 1]
  set port [lindex $argv 2]
  set group [lindex $argv 3]
  set values [lindex $argv 4]
  set state [lindex $argv 5]

  #set msg "$argv channel:$channel\nport:$port\ngroup:$group\nvalues:$values\nstate:$state"
  #puts $msg
  # tk_messageBox -message "$argv\n\n\
  #     channel:$channel\nport:$port\ngroup:$group\nvalues:$values\nstate:$state"
  set id [RLUsbPio::Open $port $group $channel]
  set res id_\'$id\'   
   
  if {$group=="PORT"} {
    set ret [RLUsbPio::SetConfig $id $state]
    append res ".cfg_$ret"
  }
  
  if {[string tolower $values] == "get"} {
    set ret [RLUsbPio::Get $id value]
    append  res ".get_${ret}_${value}"
  } else {
    ## if we need to SET a port to a few states, like 1-0-1
    foreach value $values {
      set ret [RLUsbPio::Set $id $value]
      append  res ".set_$ret"
    }  
  }
  set ret [RLUsbPio::Close $id] 
  append  res ".cls_$ret"
}
RLEH::Close

puts $res
# tk_messageBox -message "$argv\n\n$res"
exit
 