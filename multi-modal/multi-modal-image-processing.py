
import json
import requests
from PIL import Image
from io import BytesIO
from backend.node.genvm.icontract import IContract
from web3 import Web3

"""
This Multi-Modal Image Processing Contract leverages Decentralized Autonomous Compute (DAC) to perform various image 
processing tasks without invoking any LLMs (Large Language Models). 
The contract allows users to select a specific transformation type and applies the corresponding model directly on the decentralized network. 
The processing is handled entirely by the DAC, ensuring that all computations are decentralized and secure.
"""
class ImageDataManipulator(IContract):
    
    LLM_LIST = [
        ('chatgpt-3-turbo', {'resize': 8, 'score': 7, 'rotate': 6}),
        ('gpt-4', {'resize': 7, 'score': 9, 'rotate': 8}),
        ('llama-2', {'resize': 6, 'score': 8, 'rotate': 7}),
    ]
    
    def __init__(self, image_url: str, chainlink_function_url: str, transformation_type: str, target_format: str):
        """
        Initializes a new instance of the ImageDataManipulator contract.

        Args:
            image_url (str): The URL to the image to be manipulated.
            chainlink_function_url (str): The URL of the Chainlink function.
            transformation_type (str): The type of transformation to be applied (e.g., "resize", "crop", "rotate").
            target_format (str): The desired output format of the image (e.g., "jpeg", "png").
        
        Attributes:
            image_url (str): The URL to the image to be manipulated.
            transformation_type (str): The type of transformation to be applied.
            target_format (str): The desired output format of the image.
            transformed_image (str): The data of the transformed image. Default is None.
        """
        self.image_url = image_url
        self.chainlink_function_url = chainlink_function_url
        self.transformation_type = transformation_type
        self.target_format = target_format
        self.transformed_image = None
          
    def select_llm(self) -> str:
        """
        Selects the LLM with the highest score for the given transformation type.

        Returns:
            str: The name of the selected LLM.
        """
        max_score = -1
        selected_llm = None

        for llm_name, scores in self.LLM_LIST:
            score = scores.get(self.transformation_type, 0)
            if score > max_score:
                max_score = score
                selected_llm = llm_name
            elif score == max_score and selected_llm is None:
                selected_llm = llm_name

        if selected_llm is None:
            raise ValueError("No suitable LLM found for the specified transformation type.")

        return selected_llm
    
    def fetch_image(self) -> bytes:
        """
        Fetches the image data from the provided URL.

        Returns:
            bytes: The raw image data.
        """
        response = requests.get(self.image_url)
        response.raise_for_status()
        return response.content

    def process_image(self, image_data: bytes) -> bytes:
        """
        Applies the specified transformation to the image data.

        Args:
            image_data (bytes): The raw image data.
        
        Returns:
            bytes: The transformed image data.
        """
        
        selected_llm = self.select_llm()

        # Prepare the payload for the Chainlink Function request
        payload = {
            "image_data": image_data.decode('latin1'),  # Encode as string for JSON
            "transformation_type": self.transformation_type,
            "llm": selected_llm
        }

        # Call the Chainlink Function
        transformed_image_data = self.call_chainlink_function(payload)

        return transformed_image_data

    def call_chainlink_function(self, payload):
        # Prepare the transaction for the Chainlink function call
        nonce = self.web3.eth.getTransactionCount(self.account.address)
        transaction = self.contract.functions.sendImageProcessingRequest(
            payload["image_data"],
            payload["transformation_type"],
            payload["llm"],
            1,  # Replace with your subscriptionId
            100000,  # Replace with your gas limit
            Web3.toBytes(text="your_don_id")  # Replace with your DON ID
        ).buildTransaction({
            'chainId': 1,  # Replace with your chain ID
            'gas': 1000000,
            'gasPrice': self.web3.toWei('5', 'gwei'),
            'nonce': nonce,
        })

        # Sign the transaction
        signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=self.private_key)

        # Send the transaction
        tx_hash = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(f"Transaction hash: {self.web3.toHex(tx_hash)}")

        # Wait for the transaction to be mined
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        print(f"Transaction receipt: {tx_receipt}")

        # Fetch the result from the event logs or state
        # This is a placeholder. Implement logic to check for the result.
        result = self.check_result(tx_receipt)

        return result

    def convert_format(self, image_data: bytes) -> bytes:
        """
        Converts the image data to the specified format.

        Args:
            image_data (bytes): The transformed image data.
        
        Returns:
            bytes: The image data in the target format.
        """
        # Open the image from the input bytes
        image = Image.open(BytesIO(image_data))

        # Prepare a bytes buffer to hold the converted image data
        output_buffer = BytesIO()

        # Convert and save the image to the buffer in the target format
        image.save(output_buffer, format=self.target_format)

        # Get the converted image data in bytes
        converted_image_data = output_buffer.getvalue()

        # Close the buffer
        output_buffer.close()

        return converted_image_data

    async def manipulate_image(self) -> bool:
        """
        Manages the entire process of fetching, transforming, and converting the image.

        Returns:
            bool: True if the image was successfully manipulated, False otherwise.
        """
        try:
            image_data = self.fetch_image()
            transformed_image_data = self.process_image(image_data)
            self.transformed_image = self.convert_format(transformed_image_data)
            return True
        except Exception as e:
            print(f"Error processing image: {e}")
            return False
