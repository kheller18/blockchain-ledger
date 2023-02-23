# Imports
import streamlit as st
from dataclasses import dataclass
from typing import Any, List
import datetime as datetime
import pandas as pd
import hashlib


# Record class
@dataclass
class Record:
  sender: str
  receiver: str
  amount: float


# Block class
@dataclass
class Block:
    record: Record
    creator_id: int
    prev_hash: str = "0"
    timestamp: str = datetime.datetime.utcnow().strftime("%H:%M:%S")
    nonce: int = 0

    # method in Block class to hash a block
    def hash_block(self):
        sha = hashlib.sha256()

        record = str(self.record).encode()
        sha.update(record)

        creator_id = str(self.creator_id).encode()
        sha.update(creator_id)

        timestamp = str(self.timestamp).encode()
        sha.update(timestamp)

        prev_hash = str(self.prev_hash).encode()
        sha.update(prev_hash)

        nonce = str(self.nonce).encode()
        sha.update(nonce)

        return sha.hexdigest()


#PyChain class
@dataclass
class PyChain:
    chain: List[Block]
    difficulty: int = 4

    # method in Pychain class for proof of work validation
    def proof_of_work(self, block):
        calculated_hash = block.hash_block()
        num_of_zeros = "0" * self.difficulty

        while not calculated_hash.startswith(num_of_zeros):
            block.nonce += 1
            calculated_hash = block.hash_block()
        print("Wining Hash", calculated_hash)

        return block

    # method in Pychain class for adding a new block
    def add_block(self, candidate_block):
        block = self.proof_of_work(candidate_block)
        self.chain += [block]

    # method in Pychain class for validating the blockchain
    def is_valid(self):
        block_hash = self.chain[0].hash_block()

        for block in self.chain[1:]:
            if block_hash != block.prev_hash:
                print("Blockchain is invalid!")
                return False

            block_hash = block.hash_block()

        print("Blockchain is Valid")
        return True


# Streamlit Code
# Adds the cache decorator for Streamlit
@st.cache(allow_output_mutation=True)
def setup():
    print("Initializing Chain")
    return PyChain([Block("Genesis", 0)])

st.markdown("# PyChain")
st.markdown("## Store a Transaction Record in the PyChain")

pychain = setup()

# input box for sender
input_sender = st.text_input("Sender")

# input box for receiver
input_receiver = st.text_input("Receiver")

# input box for amount
input_amount = st.text_input("Amount")

# if add block button is clicked, adds block to the end of the chain and calls on both the Block and Record attributes
if st.button("Add Block"):
    prev_block = pychain.chain[-1]
    prev_block_hash = prev_block.hash_block()

    # calls on Block and Record classes to add new blocks
    new_block = Block(
        creator_id=42,
        prev_hash=prev_block_hash,
        record=Record(input_sender, input_receiver, input_amount)
    )

    pychain.add_block(new_block)
    st.balloons()

st.markdown("## The PyChain Ledger")

pychain_df = pd.DataFrame(pychain.chain).astype(str)
st.write(pychain_df)

difficulty = st.sidebar.slider("Block Difficulty", 1, 5, 2)
pychain.difficulty = difficulty

st.sidebar.write("# Block Inspector")
selected_block = st.sidebar.selectbox(
    "Which block would you like to see?", pychain.chain
)

st.sidebar.write(selected_block)

# button to validate the blockchain
if st.button("Validate Chain"):
    st.write(pychain.is_valid())
