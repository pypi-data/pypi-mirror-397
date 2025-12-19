import pytest
from dataclasses import field
from pydrafig import pydraclass, REQUIRED
from pydrafig.base_config import InvalidConfigurationError

@pydraclass
class SimpleConfig:
    lr: float = 0.01
    batch_size: int = 32
    name: str = "test"

@pydraclass
class NestedConfig:
    simple: SimpleConfig = field(default_factory=SimpleConfig)
    epochs: int = 10

def test_basic_config():
    config = SimpleConfig()
    assert config.lr == 0.01
    assert config.batch_size == 32
    assert config.name == "test"
    
    # Test valid update
    config.lr = 0.001
    assert config.lr == 0.001

def test_typo_detection():
    config = SimpleConfig()
    
    with pytest.raises(InvalidConfigurationError) as excinfo:
        config.learning_rate = 0.02
    
    msg = str(excinfo.value)
    assert "Invalid parameter 'learning_rate'" in msg
    # Should not suggest anything for 'learning_rate' vs 'lr' as distance is large, 
    # but let's test a closer typo
    
    with pytest.raises(InvalidConfigurationError) as excinfo:
        config.bacth_size = 64
    
    msg = str(excinfo.value)
    assert "Did you mean: 'batch_size'?" in msg

def test_nested_config():
    config = NestedConfig()
    assert config.simple.lr == 0.01
    
    config.simple.lr = 0.05
    assert config.simple.lr == 0.05

def test_required_field():
    @pydraclass
    class RequiredConfig:
        x: int = REQUIRED
        
    # Should probably raise error if accessed before set, or just allow it as sentinel?
    # The current implementation uses REQUIRED as a sentinel value.
    config = RequiredConfig()
    assert config.x == REQUIRED
    
    config.x = 10
    assert config.x == 10

def test_custom_finalize():
    @pydraclass
    class ValidatedConfig:
        x: int = 10
        y: int = 0
        sum: int = 0
        
        def custom_finalize(self):
            if self.x < 0:
                raise ValueError("x must be positive")
            self.sum = self.x + self.y

    config = ValidatedConfig(x=5, y=5)
    config.finalize()
    assert config.sum == 10
    
    bad_config = ValidatedConfig(x=-1)
    with pytest.raises(ValueError, match="x must be positive"):
        bad_config.finalize()

def test_recursive_finalize():
    @pydraclass
    class Leaf:
        val: int = 1
        doubled: int = 0
        def custom_finalize(self):
            self.doubled = self.val * 2

    @pydraclass
    class Node:
        leaf: Leaf = field(default_factory=Leaf)
        total: int = 0
        def custom_finalize(self):
            # Should have been finalized already
            self.total = self.leaf.doubled + 1

    config = Node()
    config.leaf.val = 5
    config.finalize()
    
    assert config.leaf.doubled == 10
    assert config.total == 11

def test_circular_dependency():
    @pydraclass
    class Node:
        child: 'Node' = None

    n1 = Node()
    n2 = Node()
    n1.child = n2
    n2.child = n1
    
    # Finalization should detect cycle
    with pytest.raises(ValueError, match="Circular reference detected"):
        n1.finalize()

def test_container_finalization():
    @pydraclass
    class Item:
        v: int = 1
        finalized: bool = False
        def custom_finalize(self):
            self.finalized = True

    @pydraclass
    class Container:
        items_list: list[Item] = field(default_factory=list)
        items_dict: dict[str, Item] = field(default_factory=dict)
    
    c = Container()
    c.items_list.append(Item())
    c.items_dict["k"] = Item()
    
    c.finalize()
    assert c.items_list[0].finalized
    assert c.items_dict["k"].finalized

