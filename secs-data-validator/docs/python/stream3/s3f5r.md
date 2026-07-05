# S3F5R - Material Found Send

**Direction:** Sent by Equipment Only

Format:

{L:2
[MF](http://hume.com/secs/items.html#MF)

[QUA](http://hume.com/secs/items.html#QUA) }


|     |     |     |

```
from dmhclient import lindex, ljoin, lsplit, RcResult

    # S3F5 Python Receive message - add next line to setup
    # sp = your SecsEquip or SecsHost connection object
    sp.messageTypeAdd( 3, 5, secs_receive_S3F5)

def secs_receive_S3F5(sp, stream:int, function:int, send_reply:bool, transactionID:int, TSN_data:str, header:str):
    '''Receive SECS Message S3F5.'''
    ok = True
    while ok:   # break out of loop on error
        # expect L:2 MF QUA
        # MF B:1 (varies)  material format code, ASCII indicates generic units, E40 restricts to B:1
        # QUA B:1 (always)  quantity (format limits max to 255!)
        pylist0 = lsplit(TSN_data)
        if len(pylist0) != 3 or pylist0[0] != "L:2":
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
        if send_reply:
            # TODO create reply message, use ljoin() to build from parts
            sp.sendReply( 3, 6, transactionID, reply_data)
        return # finished ok
    # here by break from while ok
# end recv_S3F5
```

|     |     |     |

