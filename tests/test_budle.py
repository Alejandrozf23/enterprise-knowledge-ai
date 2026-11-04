import unittest
from unittest.mock import patch
# Asegúrate de cambiar 'tu_modulo' por el nombre real de tu carpeta/archivo de origen
from tu_modulo.budle import create_batch_report


class TestCreateBatchReport(unittest.TestCase):

    def setUp(self):
        # Datos simulados de entrada y salida para la función interna
        self.mock_documents = [{"id": 1, "text": "test"}]
        self.mock_processed_result = {
            "stats": {"total_words": 10, "doc_count": 1},
            "documents": [{"id": 1, "processed": True}]
        }

    @patch('tu_modulo.budle.process_document_collection_with_stats')
    def test_success_with_default_arguments(self, mock_process):
        """Caso feliz: Verifica el comportamiento con los parámetros por defecto."""
        mock_process.return_value = self.mock_processed_result

        resultado = create_batch_report(self.mock_documents)

        self.assertEqual(resultado["name"], "default")
        self.assertEqual(resultado["stats"], self.mock_processed_result["stats"])
        self.assertEqual(resultado["metadata"], {})
        self.assertNotIn("documents", resultado)  # include_documents es False por defecto
        mock_process.assert_called_once_with(self.mock_documents)

    @patch('tu_modulo.budle.process_document_collection_with_stats')
    def test_success_including_documents_and_metadata(self, mock_process):
        """Verifica que se incluyan los documentos y la metadata adicional."""
        mock_process.return_value = self.mock_processed_result

        resultado = create_batch_report(
            self.mock_documents,
            name="  Reporte Mixto  ",  # Debe limpiarse el espacio en blanco
            include_documents=True,
            author="PC User",
            version="1.0"
        )

        self.assertEqual(resultado["name"], "Reporte Mixto")
        self.assertEqual(resultado["documents"], self.mock_processed_result["documents"])
        self.assertEqual(resultado["metadata"], {"author": "PC User", "version": "1.0"})

    def test_raise_type_error_when_name_is_not_str(self):
        """Debe lanzar TypeError si el nombre no es una cadena."""
        with self.assertRaises(TypeError) as context:
            create_batch_report(self.mock_documents, name=123)
        self.assertEqual(str(context.exception), "name debe ser str")

    def test_raise_value_error_when_name_is_empty_or_spaces(self):
        """Debe lanzar ValueError si el nombre está vacío o tiene puros espacios."""
        with self.assertRaises(ValueError) as context:
            create_batch_report(self.mock_documents, name="   ")
        self.assertEqual(str(context.exception), "name no debe estar vacío")

    def test_raise_type_error_when_include_documents_is_not_bool(self):
        """Debe lanzar TypeError si include_documents no es estrictamente booleano."""
        with self.assertRaises(TypeError) as context:
            create_batch_report(self.mock_documents, include_documents="True")
        self.assertEqual(str(context.exception), "include_documents debe ser bool")

    def test_raise_type_error_if_positional_arguments_passed_as_keyword(self):
        """Garantiza el comportamiento de la barra `/`: 'documents' solo es posicional."""
        with self.assertRaises(TypeError):
            # Esto fallará porque 'documents' no puede pasarse con nombre
            create_batch_report(documents=self.mock_documents)


if __name__ == '__main__':
    unittest.main()
