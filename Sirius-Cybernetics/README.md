# GenLayer Team Hackathon: Intelligent Contracts Challenge

We are using version 0.3.1 of the simulator

1. **Copy .env file to the root of the project and add the OpenAI API key**
2. **Start the simulator:**
   ```bash
   docker-compose up -d
   ```
3. **Open your browser and go to http://localhost:8080/**
4. **Add at least 5 validators**
5. **Run some of the built-in contracts**
6. **Add your own contracts**
7. **Have fun!** 

## Team Sirius-Cybernetics contracts

### on-chain-verifier - On-chain identity verification via social media.

We will check LinkedIn profile of a single person, since it is a professional network and people usually keep their profiles up-to-date. We could also check other social media platforms like Twitter, Facebook, etc, but it's better to use APIs for those.
   ```bash
      Example usage:
    linkedin_id = "john-doe"
    first_name = "John"
    last_name = "Doe"
    target_country = "United States"
    target_organization = "Google"
    ```

### p2p-commit-reveal - Private P2P agreements onchain.
You want to make a bet with a friend without revealing your choice beforehand.Or, you need two parties to agree on a value without external influence. This contract is for you

1. *Commit:* One party commits to a value without revealing it. They do this by hashing the value along with a secret, creating a unique fingerprint. This fingerprint is stored publicly on the blockchain.
2. *Reveal:*  Later, the party reveals their original value and secret. The contract verifies the reveal by recomputing the hash and comparing it to the stored fingerprint. 
3. *Agreement:* If the hashes match, the value is considered valid and agreed upon. If not, the reveal is rejected.

### multi-modal-image-processing
