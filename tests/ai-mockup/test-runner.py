#!/usr/bin/env python3
"""
Smart Data Extractor - AI Service Test Runner
Tests various AI services for document extraction capabilities
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple
import hashlib

# AI Service Mock Classes (will be replaced with real APIs)
class AIServiceTester:
    """Base class for testing AI extraction services"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.results = []
        
    def test_document(self, file_path: str, expected_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single document extraction"""
        start_time = time.time()
        
        # This will be replaced with actual API calls
        extracted_data = self.extract(file_path)
        
        end_time = time.time()
        
        # Calculate accuracy
        accuracy = self.calculate_accuracy(extracted_data, expected_fields)
        
        result = {
            "file": file_path,
            "service": self.service_name,
            "time_taken": end_time - start_time,
            "accuracy": accuracy,
            "extracted": extracted_data,
            "expected": expected_fields,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    def extract(self, file_path: str) -> Dict[str, Any]:
        """Override this in service-specific classes"""
        raise NotImplementedError
    
    def calculate_accuracy(self, extracted: Dict[str, Any], expected: Dict[str, Any]) -> float:
        """Calculate extraction accuracy"""
        if not expected:
            return 0.0
            
        correct = 0
        total = len(expected)
        
        for field, expected_value in expected.items():
            if field in extracted:
                # Simple string matching for now
                if str(extracted[field]).lower() == str(expected_value).lower():
                    correct += 1
                    
        return (correct / total) * 100 if total > 0 else 0.0

class GoogleDocAITester(AIServiceTester):
    """Test Google Document AI"""
    
    def __init__(self):
        super().__init__("Google Document AI")
        
    def extract(self, file_path: str) -> Dict[str, Any]:
        # TODO: Implement actual Google Doc AI call
        # For now, return mock data
        return {
            "invoice_number": "INV-2024-001",
            "date": "2024-10-15",
            "amount": "1234.56",
            "vendor": "ABC Corporation"
        }

class OpenAIVisionTester(AIServiceTester):
    """Test OpenAI GPT-4 Vision"""
    
    def __init__(self):
        super().__init__("OpenAI GPT-4 Vision")
        
    def extract(self, file_path: str) -> Dict[str, Any]:
        # TODO: Implement actual OpenAI API call
        return {
            "invoice_number": "INV-2024-001",
            "date": "October 15, 2024",
            "amount": "$1,234.56",
            "vendor": "ABC Corp"
        }

class AWSTextractTester(AIServiceTester):
    """Test AWS Textract"""
    
    def __init__(self):
        super().__init__("AWS Textract")
        
    def extract(self, file_path: str) -> Dict[str, Any]:
        # TODO: Implement actual AWS Textract call
        return {
            "invoice_number": "INV-2024-001",
            "date": "10/15/2024",
            "amount": "1234.56",
            "vendor": "ABC Corporation Ltd."
        }

class TestOrchestrator:
    """Orchestrate tests across all services"""
    
    def __init__(self):
        self.services = [
            GoogleDocAITester(),
            OpenAIVisionTester(),
            AWSTextractTester()
        ]
        self.test_results = []
        
    def run_test_suite(self, test_config_path: str):
        """Run complete test suite from config file"""
        with open(test_config_path, 'r') as f:
            test_config = json.load(f)
            
        print(f"Running test suite: {test_config['name']}")
        print(f"Testing {len(test_config['tests'])} documents across {len(self.services)} services\n")
        
        for test in test_config['tests']:
            print(f"\nTesting: {test['file']}")
            print("-" * 50)
            
            for service in self.services:
                result = service.test_document(test['file'], test['expected'])
                self.test_results.append(result)
                
                print(f"{service.service_name}: {result['accuracy']:.1f}% accurate ({result['time_taken']:.2f}s)")
        
        self.save_results()
        self.print_summary()
        
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"tests/ai-mockup/results/test_run_{timestamp}.json"
        
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
            
        print(f"\nResults saved to: {results_file}")
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        # Group by service
        service_stats = {}
        for result in self.test_results:
            service = result['service']
            if service not in service_stats:
                service_stats[service] = {
                    'total_accuracy': 0,
                    'total_time': 0,
                    'count': 0
                }
            
            service_stats[service]['total_accuracy'] += result['accuracy']
            service_stats[service]['total_time'] += result['time_taken']
            service_stats[service]['count'] += 1
        
        # Print averages
        for service, stats in service_stats.items():
            avg_accuracy = stats['total_accuracy'] / stats['count']
            avg_time = stats['total_time'] / stats['count']
            
            print(f"\n{service}:")
            print(f"  Average Accuracy: {avg_accuracy:.1f}%")
            print(f"  Average Time: {avg_time:.2f}s")
            print(f"  Documents Tested: {stats['count']}")

# Pattern Learning Tester
class PatternLearningTester:
    """Test pattern recognition and learning capabilities"""
    
    def __init__(self):
        self.patterns = {}
        
    def extract_pattern(self, document_path: str) -> str:
        """Extract structural pattern from document"""
        # Simple hash-based pattern for testing
        # In reality, this would analyze document structure
        with open(document_path, 'rb') as f:
            content = f.read()
            return hashlib.md5(content).hexdigest()[:8]
    
    def learn_from_correction(self, pattern: str, field: str, correction: Tuple[str, str]):
        """Learn from user correction"""
        if pattern not in self.patterns:
            self.patterns[pattern] = {}
            
        old_value, new_value = correction
        self.patterns[pattern][field] = {
            'old': old_value,
            'new': new_value,
            'confidence_boost': 20  # Boost confidence by 20% after correction
        }
        
    def apply_learned_patterns(self, document_path: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply learned patterns to new extraction"""
        pattern = self.extract_pattern(document_path)
        
        if pattern in self.patterns:
            for field, correction in self.patterns[pattern].items():
                if field in extracted_data and extracted_data[field] == correction['old']:
                    extracted_data[field] = correction['new']
                    extracted_data[f"{field}_confidence"] = min(100, 
                        extracted_data.get(f"{field}_confidence", 70) + correction['confidence_boost'])
                        
        return extracted_data

# Batch Processing Tester
class BatchProcessingTester:
    """Test batch processing capabilities"""
    
    def __init__(self):
        self.groups = {}
        
    def classify_documents(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """Classify documents into groups"""
        groups = {
            'invoices': [],
            'receipts': [],
            'purchase_orders': [],
            'unknown': []
        }
        
        for path in file_paths:
            # Simple classification based on filename for testing
            if 'invoice' in path.lower():
                groups['invoices'].append(path)
            elif 'receipt' in path.lower():
                groups['receipts'].append(path)
            elif 'po' in path.lower() or 'purchase' in path.lower():
                groups['purchase_orders'].append(path)
            else:
                groups['unknown'].append(path)
                
        return groups
    
    def test_batch_processing(self, file_paths: List[str]):
        """Test processing multiple documents"""
        print(f"\nBatch Processing Test: {len(file_paths)} documents")
        
        # Classify documents
        groups = self.classify_documents(file_paths)
        
        print("\nDocument Classification:")
        for doc_type, paths in groups.items():
            if paths:
                print(f"  {doc_type}: {len(paths)} documents")
        
        # Simulate parallel processing
        start_time = time.time()
        
        # In reality, these would process in parallel
        for doc_type, paths in groups.items():
            if paths:
                print(f"\nProcessing {doc_type}...")
                for path in paths:
                    # Simulate processing time
                    time.sleep(0.1)
                    print(f"  ✓ {os.path.basename(path)}")
        
        end_time = time.time()
        print(f"\nTotal batch processing time: {end_time - start_time:.2f}s")
        print(f"Average per document: {(end_time - start_time) / len(file_paths):.2f}s")

# Confidence Scoring Tester
class ConfidenceScoringTester:
    """Test confidence scoring accuracy"""
    
    def calculate_field_confidence(self, field_name: str, value: str, document_quality: str) -> float:
        """Calculate confidence score for extracted field"""
        base_confidence = 85.0
        
        # Adjust based on document quality
        quality_modifiers = {
            'clear': 0,
            'medium': -15,
            'poor': -30,
            'very_poor': -50
        }
        
        # Adjust based on field type
        field_modifiers = {
            'date': 5,  # Dates are usually easier
            'amount': 0,  # Standard difficulty
            'invoice_number': 5,  # Usually clear
            'vendor': -5,  # Can be ambiguous
            'address': -10  # Often complex
        }
        
        quality_mod = quality_modifiers.get(document_quality, 0)
        field_mod = field_modifiers.get(field_name, 0)
        
        confidence = base_confidence + quality_mod + field_mod
        
        # Add some randomness for testing
        import random
        confidence += random.uniform(-5, 5)
        
        return max(0, min(100, confidence))

def main():
    """Main test runner"""
    print("Smart Data Extractor - AI Service Testing")
    print("=" * 60)
    
    # Create test orchestrator
    orchestrator = TestOrchestrator()
    
    # Check if test config exists
    test_config_path = "tests/ai-mockup/configs/basic_test_suite.json"
    
    if os.path.exists(test_config_path):
        orchestrator.run_test_suite(test_config_path)
    else:
        print(f"Test config not found: {test_config_path}")
        print("Please create test configuration first.")
    
    # Test pattern learning
    print("\n\nPattern Learning Test")
    print("=" * 60)
    pattern_tester = PatternLearningTester()
    
    # Simulate learning from correction
    pattern = "abc123"  # Mock pattern
    pattern_tester.learn_from_correction(pattern, "vendor", ("ABC", "ABC Corporation"))
    print("Learned pattern: ABC → ABC Corporation")
    
    # Test batch processing
    print("\n\nBatch Processing Test")
    print("=" * 60)
    batch_tester = BatchProcessingTester()
    
    test_files = [
        "invoice_001.pdf", "invoice_002.pdf", "receipt_001.jpg",
        "po_001.pdf", "receipt_002.jpg", "invoice_003.pdf"
    ]
    batch_tester.test_batch_processing(test_files)
    
    # Test confidence scoring
    print("\n\nConfidence Scoring Test")
    print("=" * 60)
    confidence_tester = ConfidenceScoringTester()
    
    test_scenarios = [
        ("invoice_number", "INV-2024-001", "clear"),
        ("vendor", "ABC Corp", "poor"),
        ("amount", "1234.56", "medium"),
        ("address", "123 Main St, Suite 200", "very_poor")
    ]
    
    for field, value, quality in test_scenarios:
        confidence = confidence_tester.calculate_field_confidence(field, value, quality)
        print(f"{field} ({quality} quality): {confidence:.1f}% confidence")

if __name__ == "__main__":
    main()