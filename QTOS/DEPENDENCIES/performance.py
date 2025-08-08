#!/usr/bin/env python3
"""
QTOS Performance Monitoring Utility
"""
import time
import psutil
import os
from pathlib import Path
from functools import wraps
from helpers import YELLOW, LIGHT_GREEN, RESET, RED

# Performance tracking with memory limits
_performance_data = {
    'function_calls': {},
    'execution_times': {},
    'memory_usage': [],
    'cache_hits': {},
    'cache_misses': {}
}

# Memory limits to prevent unlimited accumulation
MAX_MEMORY_SAMPLES = 1000  # Maximum memory usage samples to keep
MAX_EXECUTION_SAMPLES = 500  # Maximum execution time samples per function
MAX_CACHE_ENTRIES = 100  # Maximum cache entries to track

def _cleanup_old_data():
    """Clean up old performance data to prevent memory bloat"""
    # Clean up memory usage samples
    if len(_performance_data['memory_usage']) > MAX_MEMORY_SAMPLES:
        # Keep only the most recent samples
        _performance_data['memory_usage'] = _performance_data['memory_usage'][-MAX_MEMORY_SAMPLES:]
    
    # Clean up execution time samples
    for func_name in _performance_data['execution_times']:
        if len(_performance_data['execution_times'][func_name]) > MAX_EXECUTION_SAMPLES:
            _performance_data['execution_times'][func_name] = _performance_data['execution_times'][func_name][-MAX_EXECUTION_SAMPLES:]
    
    # Clean up cache data if too many entries
    if len(_performance_data['cache_hits']) > MAX_CACHE_ENTRIES:
        # Keep only the most frequently used caches
        sorted_caches = sorted(_performance_data['cache_hits'].items(), 
                             key=lambda x: x[1], reverse=True)[:MAX_CACHE_ENTRIES]
        _performance_data['cache_hits'] = dict(sorted_caches)
        _performance_data['cache_misses'] = {k: _performance_data['cache_misses'].get(k, 0) 
                                           for k in _performance_data['cache_hits']}

def performance_monitor(func_name=None):
    """Decorator to monitor function performance with memory limits"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss
            
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                success = False
                raise e
            finally:
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss
                
                execution_time = end_time - start_time
                memory_delta = end_memory - start_memory
                
                # Record performance data
                name = func_name or func.__name__
                if name not in _performance_data['function_calls']:
                    _performance_data['function_calls'][name] = 0
                    _performance_data['execution_times'][name] = []
                
                _performance_data['function_calls'][name] += 1
                _performance_data['execution_times'][name].append(execution_time)
                
                # Record memory usage
                _performance_data['memory_usage'].append({
                    'timestamp': time.time(),
                    'memory': end_memory,
                    'delta': memory_delta,
                    'function': name
                })
                
                # Clean up old data periodically
                if len(_performance_data['memory_usage']) % 100 == 0:
                    _cleanup_old_data()
            
            return result
        return wrapper
    return decorator

def cache_monitor(cache_name):
    """Decorator to monitor cache performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if cache_name not in _performance_data['cache_hits']:
                _performance_data['cache_hits'][cache_name] = 0
                _performance_data['cache_misses'][cache_name] = 0
            
            # This is a simplified cache monitoring
            # In a real implementation, you'd track actual cache hits/misses
            result = func(*args, **kwargs)
            _performance_data['cache_hits'][cache_name] += 1
            
            return result
        return wrapper
    return decorator

def get_performance_stats():
    """Get comprehensive performance statistics"""
    stats = {
        'function_stats': {},
        'memory_stats': {},
        'cache_stats': {},
        'system_stats': {}
    }
    
    # Function statistics
    for func_name, calls in _performance_data['function_calls'].items():
        times = _performance_data['execution_times'].get(func_name, [])
        if times:
            stats['function_stats'][func_name] = {
                'calls': calls,
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'total_time': sum(times)
            }
    
    # Memory statistics
    if _performance_data['memory_usage']:
        memory_values = [entry['memory'] for entry in _performance_data['memory_usage']]
        stats['memory_stats'] = {
            'current': memory_values[-1] if memory_values else 0,
            'peak': max(memory_values) if memory_values else 0,
            'average': sum(memory_values) / len(memory_values) if memory_values else 0,
            'samples': len(memory_values)
        }
    
    # Cache statistics
    for cache_name in _performance_data['cache_hits']:
        hits = _performance_data['cache_hits'].get(cache_name, 0)
        misses = _performance_data['cache_misses'].get(cache_name, 0)
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        stats['cache_stats'][cache_name] = {
            'hits': hits,
            'misses': misses,
            'total': total,
            'hit_rate': hit_rate
        }
    
    # System statistics
    try:
        process = psutil.Process()
        stats['system_stats'] = {
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'num_threads': process.num_threads(),
            'open_files': len(process.open_files()),
            'connections': len(process.connections())
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        stats['system_stats'] = {'error': 'Unable to access process information'}
    
    return stats

def print_performance_report():
    """Print a formatted performance report"""
    stats = get_performance_stats()
    
    print(f"{YELLOW}=== QTOS Performance Report ==={RESET}")
    
    # Function performance
    if stats['function_stats']:
        print(f"\n{LIGHT_GREEN}Function Performance:{RESET}")
        for func_name, func_stats in stats['function_stats'].items():
            print(f"  {func_name}:")
            print(f"    Calls: {func_stats['calls']}")
            print(f"    Avg Time: {func_stats['avg_time']:.4f}s")
            print(f"    Total Time: {func_stats['total_time']:.4f}s")
    
    # Memory usage
    if stats['memory_stats']:
        print(f"\n{LIGHT_GREEN}Memory Usage:{RESET}")
        mem_stats = stats['memory_stats']
        print(f"  Current: {mem_stats['current'] / 1024:.2f} KB")
        print(f"  Peak: {mem_stats['peak'] / 1024:.2f} KB")
        print(f"  Average: {mem_stats['average'] / 1024:.2f} KB")
        print(f"  Samples: {mem_stats['samples']}")
    
    # Cache performance
    if stats['cache_stats']:
        print(f"\n{LIGHT_GREEN}Cache Performance:{RESET}")
        for cache_name, cache_stats in stats['cache_stats'].items():
            print(f"  {cache_name}:")
            print(f"    Hit Rate: {cache_stats['hit_rate']:.1f}%")
            print(f"    Hits: {cache_stats['hits']}")
            print(f"    Misses: {cache_stats['misses']}")
    
    # System statistics
    if stats['system_stats']:
        print(f"\n{LIGHT_GREEN}System Statistics:{RESET}")
        sys_stats = stats['system_stats']
        if 'error' not in sys_stats:
            print(f"  CPU Usage: {sys_stats['cpu_percent']:.1f}%")
            print(f"  Memory Usage: {sys_stats['memory_percent']:.1f}%")
            print(f"  Threads: {sys_stats['num_threads']}")
            print(f"  Open Files: {sys_stats['open_files']}")
            print(f"  Connections: {sys_stats['connections']}")
        else:
            print(f"  {RED}Error: {sys_stats['error']}{RESET}")

def clear_performance_data():
    """Clear all performance tracking data"""
    global _performance_data
    _performance_data = {
        'function_calls': {},
        'execution_times': {},
        'memory_usage': [],
        'cache_hits': {},
        'cache_misses': {}
    }
    print(f"{LIGHT_GREEN}[ INFO ] Performance data cleared{RESET}")

def force_cleanup():
    """Force cleanup of old performance data"""
    _cleanup_old_data()
    print(f"{LIGHT_GREEN}[ INFO ] Forced cleanup completed{RESET}")

def export_performance_data(filename='qtos_performance.json'):
    """Export performance data to JSON file"""
    import json
    from datetime import datetime
    
    export_data = {
        'timestamp': datetime.now().isoformat(),
        'performance_data': _performance_data,
        'stats': get_performance_stats()
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"{LIGHT_GREEN}Performance data exported to {filename}{RESET}")
    except Exception as e:
        print(f"{RED}Failed to export performance data: {e}{RESET}")

# Example usage of performance monitoring
if __name__ == '__main__':
    # Test the performance monitoring
    @performance_monitor()
    def test_function():
        time.sleep(0.1)
        return "test"
    
    # Run some test calls
    for i in range(5):
        test_function()
    
    # Print performance report
    print_performance_report() 