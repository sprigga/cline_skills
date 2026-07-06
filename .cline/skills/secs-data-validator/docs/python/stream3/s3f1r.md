# S3F1R - Material Status Request

**Direction:** Sent by Host Only

Format:

_header only_


|     |     |     |

```
from dmhclient import lindex, ljoin, lsplit, RcResult

    # S3F1R Python Receive message - add next line to setup
    # sp = your SecsEquip or SecsHost connection object
    sp.messageTypeAdd( 3, 1, secs_receive_S3F1R)

def secs_receive_S3F1R(sp, stream:int, function:int, send_reply:bool, transactionID:int, TSN_data:str, header:str):
    '''Receive SECS Message S3F1R.'''
    ok = True
    while ok:   # break out of loop on error
        # no data expected
        if send_reply:
            # TODO create reply message, use ljoin() to build from parts
            sp.sendReply( 3, 2, transactionID, reply_data)
        return # finished ok
    # here by break from while ok
    # bad data
    sp.sendS9( 7, header)
# end recv_S3F1R
```

|     |     |     |

