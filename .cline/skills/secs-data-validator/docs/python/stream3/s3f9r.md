# S3F9R - Matl ID Equate Send

**Direction:** Sent by Equipment Only

Format:

{L:2
[MID](http://hume.com/secs/items.html#MID)

[EMID](http://hume.com/secs/items.html#EMID) }


|     |     |     |

```
from dmhclient import lindex, ljoin, lsplit, RcResult

    # S3F9R Python Receive message - add next line to setup
    # sp = your SecsEquip or SecsHost connection object
    sp.messageTypeAdd( 3, 9, secs_receive_S3F9R)

def secs_receive_S3F9R(sp, stream:int, function:int, send_reply:bool, transactionID:int, TSN_data:str, header:str):
    '''Receive SECS Message S3F9R.'''
    ok = True
    while ok:   # break out of loop on error
        # expect L:2 MID EMID
        # MID A:16 (varies)  material ID, E40 restricts to A:n
        # EMID A:16 (varies)  equivalent material ID
        pylist0 = lsplit(TSN_data)
        if len(pylist0) != 3 or pylist0[0] != "L:2":
            ok = False
            break
        pylist1 = lsplit(pylist0[1])
        if len(pylist1) < 1:
            ok = False
            break
        #(typeMID, lengthMID) = pylist1[0].split(':')
        MID = (pylist1[1] if len(pylist1) == 2 else None)
        pylist1 = lsplit(pylist0[2])
        if len(pylist1) < 1:
            ok = False
            break
        #(typeEMID, lengthEMID) = pylist1[0].split(':')
        EMID = (pylist1[1] if len(pylist1) == 2 else None)
        if send_reply:
            # TODO create reply message, use ljoin() to build from parts
            sp.sendReply( 3, 10, transactionID, reply_data)
        return # finished ok
    # here by break from while ok
# end recv_S3F9R
```

|     |     |     |

