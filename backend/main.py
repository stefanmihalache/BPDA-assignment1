from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from starlette import status
from multiversx_sdk import Transaction, TransactionComputer
import time
import asyncio

from interactor.transaction_manager import TransactionManager
from interactor.models import CardProperties
from logger import LOG


app = FastAPI(
    title="BPDA Assignment 1",
    description="Api to interact with the smart contract.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TransactionManager = TransactionManager()
assigned_card = CardProperties()
card_nonce = None

@app.get("/", summary="Root Endpoint")
async def root():
    """
    Root Endpoint
    This endpoint provides a greeting message and directs users to the Swagger UI documentation for the API.
    By navigating to `/docs`, users can access the interactive API documentation where they can see all
    available endpoints, their expected parameters, and try out the API directly from the browser.
    """

    return {"message": "Welcome to the API. Check /docs for Swagger documentation."}


@app.get("/assigned/nft/", status_code=status.HTTP_200_OK, summary="Get Your Assigned NFT")
async def get_assigned_nft():
    """
    Call the getYourNftCardProperties endpoint from the smart contract to receive the properties of the NFT
    you have to trade with. The properties you receive are hex encoded.
    """

    signer = TransactionManager.get_signer()
    sender_address = TransactionManager.get_sender_address()
    contract = TransactionManager.get_contract()
    provider = TransactionManager.get_network_provider()

    sender_nonce = provider.get_account(sender_address).nonce

    tx = Transaction(
        nonce=sender_nonce,
        sender=sender_address.bech32(),
        receiver=contract.bech32(),
        value= 0,
        gas_limit= 10000000,
        data=b"getYourNftCardProperties",
        chain_id="D",
    )

    tc = TransactionComputer()
    tx.signature = signer.sign(tc.compute_bytes_for_signing(tx))

    try:
        tx_hash = provider.send_transaction(tx)

        LOG.info(f"Transaction hash: {tx_hash}")

        # wait for the transaction to initialize
        time.sleep(2)

        # start a background task to wait for the transaction to execute
        asyncio.create_task(set_card(tx_hash))

        return "Transaction successfully sent."

    except Exception as e:
        LOG.error(f"Error sending transaction: {e}")
        return {"error": str(e)}


async def set_card(tx_hash:str):
    global assigned_card

    provider = TransactionManager.get_network_provider()

    while True:
        try:
            # Get the transaction status asynchronously
            tx_on_network = provider.get_transaction(tx_hash, with_process_status=True)

            # Debug: print the current status of the transaction
            # LOG.warning(f"Transaction data: {tx_on_network.status}")
            if str(tx_on_network.status) != 'pending':
                break

            # Wait for 5 seconds before checking the status again
            await asyncio.sleep(5)


        except Exception as e:
            print(f"Error fetching transaction status: {e}")
            break


    response_data = tx_on_network.contract_results.items[0].data
    attributes = response_data.split('@')[2]

    assigned_card = CardProperties(int(attributes[1]), int(attributes[3]), int(attributes[5]))
    LOG.info(assigned_card)

    return None  # Return None if transaction did not succeed


@app.get("/smart-contract/data/", summary="Get Smart Contract Data", status_code=status.HTTP_200_OK)
async def get_smart_contract_data():
    global assigned_card
    global card_nonce

    try:
        query_controller = TransactionManager.get_query_controller()
        contract = TransactionManager.get_contract()

        query = query_controller.create_query(
            contract=contract.to_bech32(),
            function="nftSupply",
            arguments=[],
        )

        response = query_controller.run_query(query)
        data = query_controller.parse_query_response(response)

        card_list = [
            list(byte_str.split(b"\x00\x00\x00\x03")[1][:3])
            for byte_str in data
        ]

        card_nonce = -1
        card_attributes = assigned_card.to_list()

        for index, card in enumerate(card_list, start=1):
            if card == card_attributes:
                card_nonce = index
                break

        LOG.warning(card_nonce)
        return "OK"

    except Exception as e:
        LOG.error(f"Error sending transaction: {e}")
        return {"error": str(e)}