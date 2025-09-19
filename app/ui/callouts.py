import streamlit as st


class Callouts:
    @staticmethod
    def info(message: str):
        """Exibe uma mensagem de informação com ícone personalizado."""
        st.info(f"ℹ️ {message}")

    @staticmethod
    def success(message: str):
        """Exibe uma mensagem de sucesso com ícone personalizado."""
        st.success(f"✅ {message}")

    @staticmethod
    def warning(message: str):
        """Exibe uma mensagem de aviso com ícone personalizado.""" 
        st.warning(f"⚠️ {message}")

    @staticmethod
    def error(message: str):
        """Exibe uma mensagem de erro com ícone personalizado."""
        st.error(f"❌ {message}")

    @staticmethod
    def danger(message: str):
        """Exibe uma mensagem de perigo com formatação especial."""
        st.error(f"🚨 **ATENÇÃO:** {message}")
