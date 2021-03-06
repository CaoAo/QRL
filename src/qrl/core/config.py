# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
import decimal
from os.path import expanduser
from qrl import __version__ as version

import os

import yaml
from math import ceil, log


class UserConfig(object):
    __instance = None

    def __init__(self):
        # TODO: Move to metaclass in Python 3
        if UserConfig.__instance is not None:
            raise Exception("UserConfig can only be instantiated once")

        UserConfig.__instance = self

        # Default configuration
        self.mining_enabled = False
        self.mining_address = ''
        self.mining_thread_count = 0  # 0 to auto detect thread count based on CPU/GPU number of processors
        self.mining_pause = 0  # this will force a sleep (ms) while mining to reduce cpu usage. Only for mocknet

        # Ephemeral Configuration
        self.accept_ephemeral = True

        # PEER Configuration
        self.enable_peer_discovery = True  # Allows to discover new peers from the connected peers
        self.peer_list = ['104.251.219.215',
                          '104.251.219.145',
                          '104.251.219.40',
                          '104.237.3.185',
                          '35.177.60.137']
        self.p2p_local_port = 9000  # Locally binded port at which node will listen for connection
        self.p2p_public_port = 9000  # Public port forwarding connections to server

        self.peer_rate_limit = 500  # Max Number of messages per minute per peer

        self.ntp_servers = ['pool.ntp.org', 'ntp.ubuntu.com']
        self.ban_minutes = 20  # Allows to ban a peer's IP who is breaking protocol

        self.monitor_connections_interval = 30  # Monitor connection every 30 seconds
        self.max_peers_limit = 100  # Number of allowed peers
        self.chain_state_timeout = 180
        self.chain_state_broadcast_period = 30
        # must be less than ping_timeout

        self.transaction_pool_size = 25000
        self.pending_transaction_pool_size = 75000
        # 1% of the pending_transaction_pool will be reserved for moving stale txn
        self.pending_transaction_pool_reserve = int(self.pending_transaction_pool_size * 0.01)
        self.stale_transaction_threshold = 15  # 15 Blocks

        self._qrl_dir = expanduser(os.path.join("~/.qrl"))

        # ======================================
        #        ADMIN API CONFIGURATION
        # ======================================
        self.admin_api_enabled = False
        self.admin_api_host = "127.0.0.1"
        self.admin_api_port = 9008
        self.admin_api_threads = 1
        self.admin_api_max_concurrent_rpc = 100

        # ======================================
        #        PUBLIC API CONFIGURATION
        # ======================================
        self.public_api_enabled = True
        self.public_api_host = "0.0.0.0"
        self.public_api_port = 9009
        self.public_api_threads = 1
        self.public_api_max_concurrent_rpc = 100

        # ======================================
        #        MINING API CONFIGURATION
        # ======================================
        self.mining_api_enabled = False
        self.mining_api_host = "127.0.0.1"
        self.mining_api_port = 9007
        self.mining_api_threads = 1
        self.mining_api_max_concurrent_rpc = 100

        # ======================================
        #        GRPC PROXY CONFIGURATION
        # ======================================
        self.grpc_proxy_host = "127.0.0.1"
        self.grpc_proxy_port = 18090
        self.p2p_q_size = 1000
        self.outgoing_message_expiry = 90  # Outgoing message expires after 90 seconds

        # WARNING! loading should be the last line.. any new setting after this will not be updated by the config file
        self.load_yaml(self.config_path)
        # WARNING! loading should be the last line.. any new setting after this will not be updated by the config file

    @property
    def qrl_dir(self):
        return self._qrl_dir

    @qrl_dir.setter
    def qrl_dir(self, new_qrl_dir):
        self._qrl_dir = new_qrl_dir
        self.load_yaml(self.config_path)

    @property
    def wallet_dir(self):
        return expanduser(self.qrl_dir)

    @property
    def data_dir(self):
        return expanduser(os.path.join(self.qrl_dir, "data"))

    @property
    def config_path(self):
        return expanduser(os.path.join(self.qrl_dir, "config.yml"))

    @property
    def log_path(self):
        return expanduser(os.path.join(self.qrl_dir, "qrl.log"))

    @property
    def mining_pool_payment_wallet_path(self):
        return expanduser(os.path.join(self.qrl_dir, 'payment_slaves.json'))

    @staticmethod
    def getInstance():
        if UserConfig.__instance is None:
            return UserConfig()
        return UserConfig.__instance

    def load_yaml(self, file_path):
        """
        Overrides default configuration using a yaml file
        :param file_path: The path to the configuration file
        """
        if os.path.isfile(file_path):
            with open(file_path) as f:
                dataMap = yaml.safe_load(f)
                if dataMap is not None:
                    self.__dict__.update(**dataMap)


def create_path(path):
    # FIXME: Obsolete. Refactor/remove. Use makedirs from python3
    tmp_path = os.path.join(path)
    if not os.path.isdir(tmp_path):
        os.makedirs(tmp_path)


class DevConfig(object):
    __instance = None

    def __init__(self):
        super(DevConfig, self).__init__()
        # TODO: Move to metaclass in Python 3
        if DevConfig.__instance is not None:
            raise Exception("UserConfig can only be instantiated once")

        DevConfig.__instance = self

        self.version = version
        self.genesis_prev_headerhash = b'Outside Context Problem'

        ################################################################
        # Warning: Don't change following configuration.               #
        #          For QRL Developers only                             #
        ################################################################

        self.block_lead_timestamp = 30
        self.block_max_drift = 15
        self.max_future_blocks_length = 256
        self.max_margin_block_number = 32
        self.min_margin_block_number = 7

        self.public_ip = None
        self.reorg_limit = 7 * 24 * 60  # 7 days * 24 hours * 60 blocks per hour
        self.cache_frequency = 1000

        self.message_q_size = 300
        self.message_receipt_timeout = 10  # request timeout for full message
        self.message_buffer_size = 3 * 1024 * 1024  # 3 MB

        self.max_coin_supply = decimal.Decimal(105000000)
        self.coin_remaning_at_genesis = decimal.Decimal(40000000)
        self.timestamp_error = 5  # Error in second

        self.blocks_per_epoch = 100
        self.xmss_tree_height = 12
        self.slave_xmss_height = int(ceil(log(self.blocks_per_epoch * 3, 2)))
        self.slave_xmss_height += self.slave_xmss_height % 2

        # Maximum number of ots index upto which OTS index should be tracked. Any OTS index above the specified value
        # will be managed by OTS Counter
        self.max_ots_tracking_index = 4096
        self.mining_nonce_offset = 39
        self.extra_nonce_offset = 43
        self.mining_blob_size = 76

        self.ots_bitfield_size = ceil(self.max_ots_tracking_index / 8)

        self.default_nonce = 0
        self.default_account_balance = 0 * (10 ** 9)
        self.hash_buffer_size = 4
        self.minimum_minting_delay = 45  # Minimum delay in second before a block is being created
        self.mining_setpoint_blocktime = 60
        self.genesis_difficulty = 5000
        self.tx_extra_overhead = 15  # 15 bytes
        self.coinbase_address = b'\x01\x03\x00\x08#\x82\xa5/\x8b\xa9\xc2\xd3:\xd8\x07\xc2\xcd\xd5\xbd\x08l,/\xe6<n\xa1;c\r\x12\x80\x89L:9\xe1\xc3\x80'

        # Directories and files
        self.db_name = 'state'
        self.peers_filename = 'peers.qrl'
        self.chain_file_directory = 'data'
        self.wallet_dat_filename = 'wallet.json'
        self.slave_dat_filename = 'slave.qrl'
        self.banned_peers_filename = 'banned_peers.qrl'

        self.genesis_timestamp = 1524928900

        self.supplied_coins = 65000000 * (10 ** 9)

        # ======================================
        #       TRANSACTION CONTROLLER
        # ======================================
        # Max number of output addresses and corresponding data can be added into a list of a transaction
        self.transaction_multi_output_limit = 100

        # ======================================
        #          TOKEN TRANSACTION
        # ======================================
        self.max_token_symbol_length = 10
        self.max_token_name_length = 30

        # ======================================
        #       DIFFICULTY CONTROLLER
        # ======================================
        self.N_measurement = 250
        self.kp = 5

        # ======================================
        #       BLOCK SIZE CONTROLLER
        # ======================================
        self.number_of_blocks_analyze = 10
        self.size_multiplier = 1.1
        self.block_min_size_limit = 1024 * 1024  # 1 MB - Initial Block Size Limit

        # ======================================
        # SHOR PER QUANTA / MAX ALLOWED DECIMALS
        # ======================================
        self.shor_per_quanta = decimal.Decimal(10 ** 9)

        # ======================================
        #            P2P SETTINGS
        # ======================================
        self.max_receivable_bytes = 10 * 1024 * 1024  # 10 MB [Temporary Restriction]
        self.reserved_quota = 1024  # 1 KB
        self.max_bytes_out = self.max_receivable_bytes - self.reserved_quota
        self.sync_delay_mining = 60  # Delay mining by 60 seconds while syncing blocks to mainchain

        # ======================================
        #            API SETTINGS
        # ======================================
        self.block_timeseries_size = 1440

    @staticmethod
    def getInstance():
        if DevConfig.__instance is None:
            return DevConfig()
        return DevConfig.__instance


user = UserConfig.getInstance()
dev = DevConfig.getInstance()
