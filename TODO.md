# 📋 ASE Lab 24/25 Project - Gacha Game Backend: To-Do List

## Project Setup
- [x] Initialize GitHub repository and set up README with a "Get Started" section.
- [x] Configure Docker Compose for microservices architecture.
- [x] Implement REST API endpoints for each microservice.
- [x] Ensure inter-service communication via REST API.

## Testing
- [ ] **Unit Testing**:
  - [ ] Create Postman unit tests for each endpoint (test both correct and incorrect inputs).
  - [ ] Export tests as JSON files and store in `docs` folder on GitHub.
- [ ] **Performance Testing**:
  - [ ] Set up Locust tests targeting the gateway, covering main endpoints.
  - [ ] Verify rarity distribution consistency for gacha rolls under high request volumes.

## Security
- [x] **API Segmentation**: Separate admin API access on a distinct Docker network.
- [ ] **HTTPS**: Enable HTTPS for all services using self-signed certificates.
  - [ ] Self-signed cerficate creation
- [ ] **Data Encryption**: Encrypt sensitive data in the database.
- [ ] **Authentication & Authorization**:
  - [ ] Implement OAuth2 and OpenID Connect standards using JWT.
  - [ ] Validate and securely transmit "username" and "password" credentials.
- [ ] **Static & Dependency Analysis**:
  - [ ] Run automatic code analysis using language-appropriate tools.
  - [ ] Ensure Docker images are free of critical vulnerabilities.

## Documentation
- [ ] **Documentation Folder** (`docs/`):
  - [ ] Final report in PDF format.
  - [ ] OpenAPI spec file for backend REST API.
  - [ ] JSON files for Postman collections with unit tests.
  - [ ] Locust performance test files.
  - [ ] YAML file(s) for GitHub Actions workflows.

## Evaluation Criteria
- [ ] Ensure backend setup is executable with clear documentation.
- [ ] Optimize documentation for clarity and conciseness.
- [ ] Justify design choices to reflect project requirements and best practices.
- [ ] Comprehensive testing to cover main backend behaviors.
- [ ] Verify security robustness by implementing all specified measures.

---

### Additional Features (Optional for Extra Credit)
- [ ] Implement client to interact with backend for testing flows like registration & login.
- [ ] Integrate additional gacha mechanics or rare item features.

# 📋 Core Functionalities To-Do List

## Admin Functionalities (Mandatory)
- [x] **Login/Logout**: Allow admin to log in and out of the system.
- [ ] **User Management**:
  - [x] View all user accounts/profiles.
  - [ ] Access and modify specific user accounts/profiles.
  - [x] Review currency transaction history for specific players.
  - [x] Review market history for specific players.
- [x] **Gacha Collection Management**:
  - [x] Access and review the entire gacha collection.
  - [x] Modify the overall gacha collection.
  - [X] View details of specific gachas.
  - [X] Update information on specific gachas.
- [ ] **Auction Market**:
  - [x] View all active auctions.
  - [x] Access and review individual auction details.
  - [ ] Modify details of specific auctions.
  - [x] View complete auction market history.
     
## Admin Optional Functionalities
- [ ] **User Analytics**: Generate user activity reports for analysis.
- [ ] **Account Suspension**: Suspend user accounts for rule violations.
- [ ] **Custom Notifications**: Send custom notifications to specific users.
- [ ] **Enhanced Security Logs**: Track and review security-related events.
- [ ] **System Backup**: Schedule automatic backups for system data.
- [ ] **Audit Trails**: Implement audit trails for admin actions.

## Player Functionalities (Mandatory)
- [ ] **Account Management**:
  - [x] Create game account/profile.
  - [x] Delete game account/profile.
  - [ ] Modify account/profile details.
  - [x] Log in and out of the system.
  - [ ] Ensure data security for account/profile.
- [x] **Gacha Collection**:
  - [x] View personal gacha collection.
  - [x] Access details of specific gachas in personal collection.
  - [x] Browse the system's gacha collection.
  - [x] Access details of gachas in the system collection.
  - [x] Use in-game currency to roll a gacha.
- [ ] **In-Game Currency**:
  - [x] Purchase in-game currency.
  - [ ] Secure transaction processes for currency.
- [ ] **Auction Market**:
  - [x] Access the auction market.
  - [x] Set up auctions for personal gacha items.
  - [x] Place bids on gachas listed in the market.
  - [x] Review personal transaction history.
  - [x] Receive a gacha upon winning an auction.
  - [x] Receive currency when others win personal auctions.
  - [x] Refund currency if a bid is lost.
  - [ ] Ensure auction integrity and prevent tampering.
     
## Player Optional Functionalities
- [ ] **Friend List Management**: Add or remove friends in the player profile.
- [ ] **Direct Messaging**: Send and receive messages with other players.
- [ ] **Achievements**: Track and display achievements in the player's profile.
- [ ] **Leaderboards**: Access leaderboards for top players and performance.
- [ ] **In-Game Events**: Participate in scheduled in-game events.
- [ ] **Profile Customization**: Customize the appearance of player profiles.
- [ ] **Gift System**: Send gifts to other players.
- [ ] **Daily Rewards**: Claim daily login rewards.
- [ ] **Push Notifications**: Enable notifications for game updates and events.

