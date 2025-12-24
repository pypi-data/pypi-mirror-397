from sqlalchemy import create_engine, text
from sshtunnel import SSHTunnelForwarder

class Connect():

    def __init__(self, parameters: dict):
        self.params = parameters

        # Banco
        self.db_dialect = self.params["db_dialect"]
        self.db_protocol = self.params["db_protocol"] + "://"
        self.db_host = self.params["db_host"]
        self.db_port = self.params["db_port"]
        self.db_user = self.params["db_user"]
        self.db_password = self.params["db_password"]
        self.db_name = self.params["db_name"]
        self.db_driver = self.params["db_driver"] or ""

        # SSH
        self.shh = self.params.get("ssh", False)
        self.ssh_host = self.params.get("ssh_host", "")
        self.ssh_port = self.params.get("ssh_port", 22)
        self.ssh_user = self.params.get("ssh_user", "")
        self.ssh_password = self.params.get("ssh_password", "")

        # Objetos internos
        self.engine = None
        self.conn = None
        self.ssh_tunnel = None

    def __enter__(self):
        if self.shh:
            tunnel = SSHTunnelForwarder(
                (self.ssh_host, 22),
                ssh_username=self.ssh_user,
                ssh_password=self.ssh_password,
                remote_bind_address=(self.db_host, self.db_port),  # ajuste se necessário
                local_bind_address=('127.0.0.1', 0)
            )
            tunnel.start()
            self.ssh_tunnel = tunnel
            self.db_host = "127.0.0.1"
            self.db_port = self.ssh_tunnel.local_bind_port

        if self.db_dialect in ['PostgreSQL', 'SQLServer']:
            db_host = self.db_host
            db_port = self.db_port
            db_url = f"@{db_host}:{db_port}/"
            db_credentials = f"{self.db_user}:{self.db_password}"
            conn_str = f"{self.db_protocol}{db_credentials}{db_url}{self.db_name}{self.db_driver}"
            self.engine = create_engine(conn_str)
            self.conn = self.engine.connect()
            return self.conn
        

        else: raise ValueError(f"Dialect {self.db_dialect} not supported.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn: self.conn.close()
        if self.engine: self.engine.dispose()
        