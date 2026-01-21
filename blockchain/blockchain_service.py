"""
Blockchain service for logging and verifying QR code scans
"""
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from web3 import Web3
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class BlockchainService:
    """Service to interact with MedicalAccessLogger smart contract"""
    
    def __init__(self):
        """Initialize blockchain connection"""
        self.w3 = None
        self.contract = None
        self.account = None
        self.connected = False
        
        try:
            # Connect to Ethereum network
            rpc_url = getattr(settings, 'ALCHEMY_RPC_URL', None)
            if not rpc_url:
                logger.warning("ALCHEMY_RPC_URL not configured")
                return
            
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if not self.w3.is_connected():
                logger.error("Failed to connect to Ethereum network")
                return
            
            # Load account
            private_key = getattr(settings, 'BLOCKCHAIN_PRIVATE_KEY', None)
            if not private_key:
                logger.warning("BLOCKCHAIN_PRIVATE_KEY not configured")
                return
            
            self.account = self.w3.eth.account.from_key(private_key)
            
            # Load contract
            contract_address = getattr(settings, 'BLOCKCHAIN_CONTRACT_ADDRESS', None)
            if not contract_address:
                logger.warning("BLOCKCHAIN_CONTRACT_ADDRESS not configured - contract not deployed yet")
                return
            
            # Load ABI
            abi_path = Path(__file__).parent / 'contract_abi.json'
            if not abi_path.exists():
                logger.error(f"Contract ABI not found at {abi_path}")
                return
            
            with open(abi_path, 'r') as f:
                abi = json.load(f)
            
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=abi
            )
            
            self.connected = True
            logger.info(f"✓ Blockchain service initialized - Contract: {contract_address}")
            
        except Exception as e:
            logger.error(f"Failed to initialize blockchain service: {str(e)}")
            self.connected = False
    
    def is_connected(self):
        """Check if blockchain service is connected"""
        return self.connected and self.w3 and self.w3.is_connected()
    
    def get_balance(self):
        """Get account ETH balance"""
        if not self.is_connected():
            return None
        
        try:
            balance_wei = self.w3.eth.get_balance(self.account.address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return None
    
    def _hash_identifier(self, identifier):
        """Create a hash of an identifier for privacy"""
        return self.w3.keccak(text=str(identifier))
    
    def log_qr_scan(self, doctor_id, patient_id, access_granted=True, metadata=None):
        """
        Log a QR code scan to the blockchain
        
        Args:
            doctor_id: Doctor's user ID
            patient_id: Patient's user ID  
            access_granted: Whether access was granted
            metadata: Optional metadata dict
            
        Returns:
            dict with transaction details or None if failed
        """
        if not self.is_connected():
            logger.warning("Blockchain not connected - scan not logged to blockchain")
            return None
        
        try:
            # Hash identifiers for privacy
            doctor_hash = self._hash_identifier(doctor_id)
            patient_hash = self._hash_identifier(patient_id)
            
            # Convert metadata to JSON string
            ipfs_metadata = json.dumps(metadata) if metadata else ""
            
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # Estimate gas
            gas_estimate = self.contract.functions.logAccess(
                doctor_hash,
                patient_hash,
                access_granted,
                ipfs_metadata
            ).estimate_gas({'from': self.account.address})
            
            # Build transaction
            transaction = self.contract.functions.logAccess(
                doctor_hash,
                patient_hash,
                access_granted,
                ipfs_metadata
            ).build_transaction({
                'chainId': self.w3.eth.chain_id,
                'from': self.account.address,
                'nonce': nonce,
                'gas': int(gas_estimate * 1.2),  # Add 20% buffer
                'gasPrice': self.w3.eth.gas_price,
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                private_key=self.account.key
            )
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Ensure tx_hash has 0x prefix for Etherscan
            tx_hash_hex = tx_hash.hex() if tx_hash.hex().startswith('0x') else f"0x{tx_hash.hex()}"
            logger.info(f"✓ QR scan transaction sent - TX: {tx_hash_hex}")
            
            # Return immediately with tx hash (don't wait for confirmation)
            result = {
                'success': True,
                'transaction_hash': tx_hash_hex,
                'pending': True,
                'explorer_url': f"https://sepolia.etherscan.io/tx/{tx_hash_hex}"
            }
            
            # Try to get receipt (with short timeout for quick response)
            try:
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=5)
                
                # Parse logs to get logId
                log_id = None
                if tx_receipt.logs:
                    # Decode the AccessLogged event
                    event_signature = self.w3.keccak(text="AccessLogged(uint256,bytes32,bytes32,uint256,bool)")
                    for log in tx_receipt.logs:
                        if log.topics[0] == event_signature:
                            # The logId is the first indexed parameter (topics[1])
                            log_id = int.from_bytes(log.topics[1], byteorder='big')
                            break
                
                # Update result with confirmed data
                result.update({
                    'pending': False,
                    'block_number': tx_receipt.blockNumber,
                    'log_id': log_id,
                    'gas_used': tx_receipt.gasUsed,
                    'confirmed': True
                })
                logger.info(f"✓ Transaction confirmed in block {tx_receipt.blockNumber}")
                
            except Exception as e:
                # Transaction sent but not yet confirmed - that's OK!
                logger.info(f"Transaction pending confirmation: {tx_hash_hex}")
                logger.warning(f"Transaction sent but receipt timeout: {str(e)}")
            
            # Return result (either confirmed or pending)
            return result
            
        except Exception as e:
            logger.error(f"Error logging to blockchain: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_access(self, log_id, doctor_id, patient_id):
        """
        Verify an access log on the blockchain
        
        Args:
            log_id: Blockchain log ID
            doctor_id: Doctor's user ID
            patient_id: Patient's user ID
            
        Returns:
            bool indicating if access is valid
        """
        if not self.is_connected():
            logger.warning("Blockchain not connected")
            return False
        
        try:
            doctor_hash = self._hash_identifier(doctor_id)
            patient_hash = self._hash_identifier(patient_id)
            
            is_valid = self.contract.functions.verifyAccess(
                log_id,
                doctor_hash,
                patient_hash
            ).call()
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying access: {str(e)}")
            return False
    
    def get_patient_scans(self, patient_id):
        """
        Get all blockchain log IDs for a patient
        
        Args:
            patient_id: Patient's user ID
            
        Returns:
            list of log IDs
        """
        if not self.is_connected():
            return []
        
        try:
            patient_hash = self._hash_identifier(patient_id)
            log_ids = self.contract.functions.getPatientLogs(patient_hash).call()
            return log_ids
        except Exception as e:
            logger.error(f"Error getting patient scans: {str(e)}")
            return []
    
    def get_doctor_scans(self, doctor_id):
        """
        Get all blockchain log IDs for a doctor
        
        Args:
            doctor_id: Doctor's user ID
            
        Returns:
            list of log IDs
        """
        if not self.is_connected():
            return []
        
        try:
            doctor_hash = self._hash_identifier(doctor_id)
            log_ids = self.contract.functions.getDoctorLogs(doctor_hash).call()
            return log_ids
        except Exception as e:
            logger.error(f"Error getting doctor scans: {str(e)}")
            return []
    
    def get_access_log(self, log_id):
        """
        Get access log details from blockchain
        
        Args:
            log_id: Blockchain log ID
            
        Returns:
            dict with log details
        """
        if not self.is_connected():
            return None
        
        try:
            log_data = self.contract.functions.getAccessLog(log_id).call()
            
            return {
                'doctor_hash': log_data[0].hex(),
                'patient_hash': log_data[1].hex(),
                'timestamp': log_data[2],
                'access_hash': log_data[3].hex(),
                'access_granted': log_data[4],
                'metadata': log_data[5]
            }
        except Exception as e:
            logger.error(f"Error getting access log: {str(e)}")
            return None
    
    def get_total_logs(self):
        """Get total number of logs on blockchain"""
        if not self.is_connected():
            return 0
        
        try:
            return self.contract.functions.getTotalLogs().call()
        except Exception as e:
            logger.error(f"Error getting total logs: {str(e)}")
            return 0


# Singleton instance
_blockchain_service = None

def get_blockchain_service():
    """Get or create blockchain service singleton"""
    global _blockchain_service
    if _blockchain_service is None:
        _blockchain_service = BlockchainService()
    return _blockchain_service
