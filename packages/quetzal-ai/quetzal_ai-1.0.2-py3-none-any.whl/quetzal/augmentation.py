"""
Advanced Data Augmentation Techniques for Low-Resource Languages
Quetzal - Powered by Axya-Tech

Specialized techniques to maximize model accuracy with minimal data
"""

import random
from typing import List, Dict, Any
import re


class LowResourceAugmenter:
    """
    Advanced augmentation strategies specifically designed for
    low-resource languages like Dhivehi
    """
    
    def __init__(self, language: str = "dhivehi"):
        self.language = language
        self.augmentation_stats = {
            "original": 0,
            "synonym_replacement": 0,
            "random_insertion": 0,
            "random_swap": 0,
            "sentence_permutation": 0,
            "code_mixing": 0,
        }
    
    def synonym_replacement(self, text: str, n: int = 1) -> str:
        """
        Replace n words with their synonyms (language-specific)
        For Dhivehi, this would use a Dhivehi synonym dictionary
        """
        words = text.split()
        
        # Placeholder: Replace with actual Dhivehi synonym logic
        # For demonstration, we'll randomly select words to "replace"
        if len(words) > n:
            indices = random.sample(range(len(words)), min(n, len(words)))
            # In production, replace with actual synonyms
            # words[idx] = get_dhivehi_synonym(words[idx])
        
        return ' '.join(words)
    
    def random_insertion(self, text: str, n: int = 1) -> str:
        """
        Randomly insert n common words into the sentence
        """
        words = text.split()
        
        # Common Dhivehi words/particles to insert
        common_words = ["އަދި", "ނަމަވެސް", "ވެސް", "އެވެ"]
        
        for _ in range(n):
            if words:
                insert_pos = random.randint(0, len(words))
                words.insert(insert_pos, random.choice(common_words))
        
        return ' '.join(words)
    
    def random_swap(self, text: str, n: int = 1) -> str:
        """
        Randomly swap n pairs of words
        """
        words = text.split()
        
        for _ in range(n):
            if len(words) >= 2:
                idx1, idx2 = random.sample(range(len(words)), 2)
                words[idx1], words[idx2] = words[idx2], words[idx1]
        
        return ' '.join(words)
    
    def sentence_permutation(self, text: str) -> str:
        """
        For multi-sentence text, permute the order
        """
        # Split by Dhivehi sentence enders
        sentences = re.split(r'[.!?؟]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) > 1:
            random.shuffle(sentences)
        
        return '. '.join(sentences)
    
    def code_mixing_augmentation(self, text: str, target_lang: str = "english") -> str:
        """
        Simulate code-mixing (common in multilingual speakers)
        Mix in words from another language
        """
        # For Dhivehi, might mix with English or Arabic
        # Placeholder implementation
        return text
    
    def augment_text(
        self, 
        text: str, 
        techniques: List[str] = None,
        augmentation_factor: int = 3
    ) -> List[str]:
        """
        Apply multiple augmentation techniques
        
        Args:
            text: Original text
            techniques: List of techniques to apply
            augmentation_factor: How many augmented versions to create
        
        Returns:
            List of augmented texts including original
        """
        
        if techniques is None:
            techniques = [
                'synonym_replacement',
                'random_insertion',
                'random_swap',
            ]
        
        augmented = [text]  # Always include original
        self.augmentation_stats["original"] += 1
        
        for _ in range(augmentation_factor - 1):
            technique = random.choice(techniques)
            
            if technique == 'synonym_replacement':
                aug_text = self.synonym_replacement(text, n=2)
                self.augmentation_stats["synonym_replacement"] += 1
            elif technique == 'random_insertion':
                aug_text = self.random_insertion(text, n=1)
                self.augmentation_stats["random_insertion"] += 1
            elif technique == 'random_swap':
                aug_text = self.random_swap(text, n=2)
                self.augmentation_stats["random_swap"] += 1
            elif technique == 'sentence_permutation':
                aug_text = self.sentence_permutation(text)
                self.augmentation_stats["sentence_permutation"] += 1
            else:
                aug_text = text
            
            augmented.append(aug_text)
        
        return augmented
    
    def augment_dataset(
        self, 
        dataset: List[Dict[str, Any]], 
        augmentation_factor: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Augment an entire dataset
        
        Args:
            dataset: List of data dictionaries
            augmentation_factor: Multiplication factor for data
        
        Returns:
            Augmented dataset
        """
        
        augmented_dataset = []
        
        for item in dataset:
            text = item.get('text', str(item))
            
            augmented_texts = self.augment_text(
                text, 
                augmentation_factor=augmentation_factor
            )
            
            for aug_text in augmented_texts:
                new_item = item.copy()
                new_item['text'] = aug_text
                augmented_dataset.append(new_item)
        
        return augmented_dataset
    
    def print_stats(self):
        """Print augmentation statistics"""
        print("\n📊 Augmentation Statistics:")
        total = sum(self.augmentation_stats.values())
        for technique, count in self.augmentation_stats.items():
            percentage = (count / total * 100) if total > 0 else 0
            print(f"   {technique}: {count} ({percentage:.1f}%)")


class ActiveLearningSelector:
    """
    Select most informative samples for training
    to maximize learning with minimal data
    """
    
    @staticmethod
    def uncertainty_sampling(
        model, 
        tokenizer, 
        unlabeled_data: List[str], 
        n_samples: int = 10
    ) -> List[str]:
        """
        Select samples where the model is most uncertain
        """
        # Placeholder for uncertainty-based selection
        # In production, calculate model entropy/confidence
        return random.sample(unlabeled_data, min(n_samples, len(unlabeled_data)))
    
    @staticmethod
    def diversity_sampling(
        unlabeled_data: List[str], 
        n_samples: int = 10
    ) -> List[str]:
        """
        Select diverse samples to cover different linguistic patterns
        """
        # Placeholder for diversity-based selection
        # In production, use embeddings and clustering
        return random.sample(unlabeled_data, min(n_samples, len(unlabeled_data)))


class SyntheticDataGenerator:
    """
    Generate synthetic training data for low-resource languages
    """
    
    def __init__(self, language: str = "dhivehi"):
        self.language = language
    
    def generate_templates(self, n: int = 100) -> List[str]:
        """
        Generate template-based synthetic sentences
        """
        # Dhivehi sentence templates
        templates = [
            "އަހަރެން ބޭނުންވަނީ {object}",
            "{subject} އަކީ {adjective} ބައެކެވެ",
            "މިއަދު {weather} ދުވަހެކެވެ",
            "{person} {action} ކުރަނީ",
        ]
        
        # Vocabulary for slots
        objects = ["ކާން", "ބޯން", "ކިޔަން", "ހިނގަން"]
        subjects = ["މި ފޮތް", "މި މީހާ", "މި ތަން"]
        adjectives = ["ރަނގަޅު", "ފުރިހަމަ", "ހީވާ"]
        
        synthetic_sentences = []
        
        for _ in range(n):
            template = random.choice(templates)
            
            # Fill template slots
            sentence = template.format(
                object=random.choice(objects),
                subject=random.choice(subjects),
                adjective=random.choice(adjectives),
                weather=random.choice(["ހޫނު", "ފިނި"]),
                person=random.choice(["އަހަރެން", "އޭނާ"]),
                action=random.choice(["މަސައްކަތް", "ކަސްރަތު"])
            )
            
            synthetic_sentences.append(sentence)
        
        return synthetic_sentences
    
    def generate_from_rules(self, grammar_rules: Dict, n: int = 50) -> List[str]:
        """
        Generate sentences based on grammar rules
        """
        # Implement context-free grammar generation
        # Placeholder implementation
        return []


# Export classes
__all__ = [
    'LowResourceAugmenter',
    'ActiveLearningSelector',
    'SyntheticDataGenerator',
]
