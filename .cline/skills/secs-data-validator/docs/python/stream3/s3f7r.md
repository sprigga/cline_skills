# S3F7R - Material Lost Send

**Direction:** Sent by Equipment Only

Format:

{L:3
[MF](http://hume.com/secs/items.html#MF)

[QUA](http://hume.com/secs/items.html#QUA)

[MID](http://hume.com/secs/items.html#MID) }


|     |     |     |

```
from dmhclient import lindex, ljoin, lsplit, RcResult

    # S3F7 Python Receive message - add next line to setup
    # sp = your SecsEquip or SecsHost connection object
    sp.messageTypeAdd( 3, 7, secs_receive_S3F7)

def secs_receive_S3F7(sp, stream:int, function:int, send_reply:bool, transactionID:int, TSN_data:str, header:str):
    '''Receive SECS Message S3F7.'''
    ok = True
    while ok:   # break out of loop on error
        # expect L:3 MF QUA MID
        # MF B:1 (varies)  material format code, ASCII indicates generic units, E40 restricts to B:1
        # QUA B:1 (always)  quantity (format limits max to 255!)
        # MID A:16 (varies)  material ID, E40 restricts to A:n
        pylist0 = lsplit(TSN_data)
        if len(pylist0) != 4 or pylist0[0] != "L:3":
            ok = False
            break
        pylist1 = lsplit(pylist0[1])
        if len(pylist1) < 1:
            ok = False
            break
        #(typeMF, lengthMF) = pylist1[0].split(':')
        MF = (pylist1[1] if len(pylist1) == 2 else None)
        pylist1 = lsplit(pylist0[2])
        if len(pylist1) < 1 or pylist1[0] != "B:1":
            ok = False
            break
        QUA = sp.binToInt(pylist1[1])
        pylist1 = lsplit(pylist0[3])
        if len(pylist1) < 1:
            ok = False
            break
        #(typeMID, lengthMID) = pylist1[0].split(':')
        MID = (pylist1[1] if len(pylist1) == 2 else None)
        if send_reply:
            # TODO create reply message, use ljoin() to build from parts
            sp.sendReply( 3, 8, transactionID, reply_data)
        return # finished ok
    # here by break from while ok
# end recv_S3F7
```

|     |     |     |

