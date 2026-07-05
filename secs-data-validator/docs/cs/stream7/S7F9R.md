# S7F9R - Matl/Process Matrix Request

**Source:** [SECS-II Automated Code Generation Tool](http://hume.com/secs/msgsCS.html)

**Sent by:** Host and Equipment

## Format

_header only_

## Details

Request for the material/process matrix. No data items in the request.

## C# Code

```csharp
    // S7F9R C# Receive message - add next line to setup
    //sp is a SecsPort or SecsHost object reference
    sp.MessageTypeAdd( 7, 9, new SecsMsgReceiveDelegate(recv_S7F9R));

// receive method
void recv_S7F9R(object sender, int stream, int function, bool send_reply, int transID, string TSN_data, string header) {
    //SecsPort sp = (SecsPort)sender;
    //SecsHost sp = (SecsHost)sender;
    bool ok=true;
    while (ok) {   // break out of loop on error
        // no data expected
        if (send_reply) {
            string reply; // TBD create reply
            sp.SendReply(7, 10, transID, reply);
            }
        return;
        } // end while(ok)
    } // end recv_S7F9R
```
