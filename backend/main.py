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
assigned_card = None
card_nonce = None
hash_collection = None
collection = None
hash_nft_create = None
nft_nonce = None
hash_nft_transfer = None

@app.get("/", summary="Root Endpoint")
async def root():
    """
    Root Endpoint
    This endpoint provides a greeting message and directs users to the Swagger UI documentation for the API.
    By navigating to `/docs`, users can access the interactive API documentation where they can see all
    available endpoints, their expected parameters, and try out the API directly from the browser.
    """

    return {"message": "Welcome to the API. Check /docs for Swagger documentation."}


async def wait_tx_finished(tx_hash:str):
    provider = TransactionManager.get_network_provider()

    while True:
        try:
            # Get the transaction status asynchronously
            tx_on_network = provider.get_transaction(tx_hash, with_process_status=True)

            # Debug: print the current status of the transaction
            # LOG.warning(f"Transaction data: {tx_on_network.status}")
            if str(tx_on_network.status) != 'pending':
                return tx_on_network
            # Wait for 5 seconds before checking the status again
            await asyncio.sleep(5)

        except Exception as e:
            print(f"Error fetching transaction status: {e}")
            break


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

    tx_on_network = await wait_tx_finished(tx_hash)

    response_data = tx_on_network.contract_results.items[0].data
    attributes = response_data.split('@')[2]
    assigned_card = CardProperties(int(attributes[1]), int(attributes[3]), int(attributes[5]))
    LOG.info(assigned_card)

    return None


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

        if not assigned_card:
            LOG.info("No card has been assigned")
            return {"data": f"{data}"}

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

        LOG.info(f"Card nonce: {card_nonce}")
        return {"card_list": card_list, "card_nonce": card_nonce}

    except Exception as e:
        LOG.error(f"Error sending transaction: {e}")
        return {"error": str(e)}


@app.post("/collection/", summary="Create NFT Collection", status_code=status.HTTP_200_OK)
async def create_nft_collection():
    global hash_collection

    signer = TransactionManager.get_signer()
    sender_address = TransactionManager.get_sender_address()
    provider = TransactionManager.get_network_provider()
    metachain_address = TransactionManager.get_metachain_address()
    collection_name = TransactionManager.get_collection_name()
    collection_ticker = TransactionManager.get_collection_ticker()

    sender_nonce = provider.get_account(sender_address).nonce
    data = (
        f"issueNonFungible@{collection_name.encode('utf-8').hex()}"
        f"@{collection_ticker.encode('utf-8').hex()}"
    )

    try:

        tx = Transaction(
            nonce=sender_nonce,
            sender=sender_address.bech32(),
            receiver=metachain_address.bech32(),
            value=50000000000000000,
            gas_limit=500000000,
            data=data.encode("UTF-8"),
            chain_id="D",
        )

        tc = TransactionComputer()
        tx.signature = signer.sign(tc.compute_bytes_for_signing(tx))
        hash_collection = provider.send_transaction(tx)

        LOG.info(f"Collection transaction hash: {hash_collection}")
        return "Transaction successfully sent."

    except Exception as e:
        LOG.error(f"Error creating collection: {e}")
        return {"error": str(e)}


@app.get("/collection/", summary="Get NFT Collection", status_code=status.HTTP_200_OK)
async def get_nft_collection():
    global hash_collection
    global collection

    if not hash_collection:
        LOG.info("No collection tx has been made")
        return {"error": "No collection tx has been made"}

    tx_on_network = await wait_tx_finished(hash_collection)
    response_data = tx_on_network.contract_results.items

    collection = next(
        (
            bytes.fromhex(item.data.split("@")[1]).decode("UTF-8")
            for item in response_data
            if "ESDTSetTokenType" in item.data
        ),
        None
    )

    LOG.info(f"Collection: {collection}")

    return "OK"


@app.post('/collection/add-roles/', summary="Add Roles", status_code=status.HTTP_200_OK)
async def add_roles():
    global collection

    if not collection:
        LOG.info("No collection has been assigned")
        return {"error": "No collection has been created"}

    signer = TransactionManager.get_signer()
    sender_address = TransactionManager.get_sender_address()
    provider = TransactionManager.get_network_provider()
    metachain_address = TransactionManager.get_metachain_address()

    sender_nonce = provider.get_account(sender_address).nonce

    ESDTRoleNFTCreate = "45534454526f6c654e4654437265617465"

    data = (
        f"setSpecialRole@{collection.encode('utf-8').hex()}"
        f"@{sender_address.hex()}"
        f"@{ESDTRoleNFTCreate}"
    )

    try:

        tx = Transaction(
            nonce=sender_nonce,
            sender=sender_address.bech32(),
            receiver=metachain_address.bech32(),
            value=0,
            gas_limit=60000000,
            data=data.encode("utf-8"),
            chain_id="D",
        )

        tc = TransactionComputer()
        tx.signature = signer.sign(tc.compute_bytes_for_signing(tx))
        hash_role_assignment = provider.send_transaction(tx)

        LOG.info(f"Role assignment transaction hash: {hash_role_assignment}")
        return "Transaction successfully sent."

    except Exception as e:
        LOG.error(f"Error assigning role to the collection: {e}")
        return {"error": str(e)}


@app.post('/nft/', summary="Create NFT", status_code=status.HTTP_200_OK)
async def create_nft():
    global assigned_card
    global collection
    global hash_nft_create

    if not assigned_card:
        LOG.info("No card has been assigned")
        return {"error": "No card has been assigned"}

    if not collection:
        LOG.info("No collection has been assigned")
        return {"error": "No collection has been created"}

    NFT_NAME = TransactionManager.get_nft_name()
    signer = TransactionManager.get_signer()
    sender_address = TransactionManager.get_sender_address()
    provider = TransactionManager.get_network_provider()

    sender_nonce = provider.get_account(sender_address).nonce

    card_attributes = assigned_card.to_list()

    quantity = 1
    royalties = f"{2500:04x}"
    hash_field = ""
    attributes = f"{card_attributes[0]:02x}{card_attributes[1]:02x}{card_attributes[2]:02x}"
    URI = "https://upload.wikimedia.org/wikipedia/commons/5/59/Monet_-_Impression%2C_Sunrise.jpg"

    data = (
        f"ESDTNFTCreate@{collection.encode('utf-8').hex()}"
        f"@{quantity:02x}"
        f"@{NFT_NAME.encode('utf-8').hex()}"
        f"@{royalties}"
        f"@{hash_field}"
        f"@{attributes}"
        f"@{URI.encode('utf-8').hex()}"
    )

    try:
        tx = Transaction(
            nonce=sender_nonce,
            sender=sender_address.bech32(),
            receiver=sender_address.bech32(),
            value=0,
            gas_limit=10000000 + len(data) * 1500,
            data=data.encode("UTF-8"),
            chain_id='D'
        )

        tc = TransactionComputer()
        tx.signature = signer.sign(tc.compute_bytes_for_signing(tx))
        hash_nft_create = provider.send_transaction(tx)

        return "OK"

    except Exception as e:
        LOG.error(f"Error creating the NFT: {e}")
        return {"error": str(e)}


@app.get("/nft/", summary="Get NFT", status_code=status.HTTP_200_OK)
async def get_nft():
    global hash_nft_create
    global nft_nonce

    if not hash_nft_create:
        LOG.info("No NFT has been assigned")
        return {"error": "No NFT has been assigned"}

    tx_on_network = await wait_tx_finished(hash_nft_create)

    response = tx_on_network.contract_results.items[0].data

    nft_nonce = response.split("@")[2]

    LOG.info(f"NFT nonce: {nft_nonce}")

    return "OK"


@app.post("/nft/exchange/", summary="Exchange NFT", status_code=status.HTTP_200_OK)
async def exchange_nft():
    global nft_nonce
    global card_nonce
    global collection

    if not nft_nonce:
        LOG.info("No NFT has been assigned")
        return {"error": "No NFT has been assigned"}

    if not collection:
        LOG.info("No collection has been assigned")
        return {"error": "No collection has been created"}

    signer = TransactionManager.get_signer()
    sender_address = TransactionManager.get_sender_address()
    contract = TransactionManager.get_contract()
    provider = TransactionManager.get_network_provider()

    sender_nonce = provider.get_account(sender_address).nonce

    metadata = "exchangeNft".encode("utf-8").hex()

    data = (
        f"ESDTNFTTransfer@{collection.encode('utf-8').hex()}"
        f"@{nft_nonce}"
        f"@{1:02x}"
        f"@{contract.hex()}"
        f"@{metadata}"
        f"@{card_nonce:02x}"
    )

    tx = Transaction(
        nonce=sender_nonce,
        sender=sender_address.bech32(),
        receiver=sender_address.bech32(),
        value=0,
        gas_limit=40000000 + len(data) * 1500,
        chain_id='D',
        data=data.encode("UTF-8")
    )

    tc = TransactionComputer()
    tx.signature = signer.sign(tc.compute_bytes_for_signing(tx))
    hash_nft_transfer = provider.send_transaction(tx)

    LOG.info(f"NFT transfer: {hash_nft_transfer}")
    return "OK"