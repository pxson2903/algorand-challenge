import os 
from pyteal import *

"""Holder Application"""

def approval_program():

   handle_creation = Seq([
       App.globalPut(Bytes("HolderOne"), Bytes("5F4U7JNC6FL667MTE3D5MCXWNKYSDOZDYKOFRVFVDS7CPDDBJ33LR5BLZZ")), 
       App.globalPut(Bytes("HolderTwo"), Bytes("5EEU7JNC6FL667MTE3D5MCXWNKYSDOZDYKOFRVFVDS7CPDDBJ33LR5BLZI")), 
       App.globalPut(Bytes("HolderThree"), Bytes("5DDU7JNC6FL667MTE3D5MCXWNKYSDOZDYKOFRVFVDS7CPDDBJ33LR5BLZI")), 
       App.globalPut(Bytes("HolderFour"), Bytes("5BBU7JNC6FL667MTE3D5MCXWNKYSDOZDYKOFRVFVDS7CPDDBJ33LR5BLZI")), 
       App.globalPut(Bytes("HolderFive"), Bytes("5CCU7JNC6FL667MTE3D5MCXWNKYSDOZDYKOFRVFVDS7CPDDBJ33LR5BLZI")), 

       App.globalPut(Bytes("HolderOneAmt"), Int(20)), 
       App.globalPut(Bytes("HolderTwoAmt"), Int(15)), 
       App.globalPut(Bytes("HolderThreeAmt"), Int(40)), 
       App.globalPut(Bytes("HolderFourAmt"), Int(15)), 
       App.globalPut(Bytes("HolderFiveAmt"), Int(10)), 
       Approve()
   ])
   handle_optin = Return(Int(0))     
   handle_closeout = Return(Int(0))
   handle_updateapp = Return(Int(1)) 
   handle_deleteapp = Return(Int(1)) 
   
   program = Cond(
       [Txn.application_id() == Int(0), handle_creation],
       [Txn.on_completion() == OnComplete.OptIn, handle_optin],
       [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
       [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
       [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
   )
   return compileTeal(program, Mode.Application, version=5)

def clear_state_program():
   program = Return(Int(1))
   return compileTeal(program, Mode.Application, version=5)

# print out the results
if __name__ == "__main__":

    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path,"11_approval.teal"), "w") as f:
        f.write(approval_program())

    with open(os.path.join(path, "11_clear.teal"), "w") as f:
        f.write(clear_state_program())