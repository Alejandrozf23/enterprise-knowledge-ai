import unittest
from unittest.mock import patch, MagicMock

# Asumiendo que el código de la imagen está en un archivo llamado batch_validator.py
from batch_validator import make_batch_validator


class TestMakeBatchValidator(unittest.TestCase):

    # 1. Validar que la fábrica genera una función correctamente
    def test_returns_callable_function(self):
        """Verifica que make_batch_validator devuelva una función ejecutable."""
        validator = make_batch_validator()
        self.assertTrue(callable(validator))

    # 2. Validar el control de tipos (TypeError)
    def test_reject_duplicates_type_error(self):
        """Debe lanzar un TypeError si reject_duplicates no es un booleano."""
        with self.assertRaises(TypeError) as context:
            make_batch_validator(reject_duplicates="True")  # Enviando string en vez de bool

        self.assertEqual(str(context.exception), "reject_duplicates debe ser bool")

    # 3. Validar el comportamiento con el argumento por defecto (False)
    @patch('batch_validator.validate_document_batch')
    def test_validator_with_default_arguments(self, mock_validate):
        """Verifica que el validador use reject_duplicates=False por defecto."""
        # Configurar el mock
        mock_validate.return_value = True

        # Crear y ejecutar el validador
        validator = make_batch_validator()
        test_docs = ["doc1", "doc2"]
        result = validator(test_docs)

        # Comprobaciones
        mock_validate.assert_called_once_with(test_docs, reject_duplicates=False)
        self.assertTrue(result)

    # 4. Validar el comportamiento cuando se activa reject_duplicates=True
    @patch('batch_validator.validate_document_batch')
    def test_validator_with_reject_duplicates_true(self, mock_validate):
        """Verifica que el validador pase reject_duplicates=True correctamente."""
        mock_validate.return_value = {"status": "success"}

        validator = make_batch_validator(reject_duplicates=True)
        test_docs = ["doc1", "doc1"]
        result = validator(test_docs)

        mock_validate.assert_called_once_with(test_docs, reject_duplicates=True)
        self.assertEqual(result, {"status": "success"})


if __name__ == '__main__':
    unittest.main()
