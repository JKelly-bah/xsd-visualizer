// XSD Documentation Interactive Features

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive features
    initializeNavigation();
    initializeSearch();
    initializeExpandableElements();
    initializeTooltips();
});

function initializeNavigation() {
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Highlight current section in navigation
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.main-nav a[href^="#"]');
    
    function highlightCurrentSection() {
        const scrollPosition = window.scrollY + 100;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }
    
    window.addEventListener('scroll', highlightCurrentSection);
    highlightCurrentSection(); // Initial call
}

function initializeSearch() {
    // Add search functionality if search box exists
    const searchInput = document.querySelector('#search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            filterElements(searchTerm);
        });
    }
    
    // Add quick filter buttons
    addQuickFilters();
}

function filterElements(searchTerm) {
    const cards = document.querySelectorAll('.element-card, .type-card');
    
    cards.forEach(card => {
        const title = card.querySelector('h3').textContent.toLowerCase();
        const documentation = card.querySelector('.documentation');
        const docText = documentation ? documentation.textContent.toLowerCase() : '';
        
        if (title.includes(searchTerm) || docText.includes(searchTerm)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}

function addQuickFilters() {
    const sections = document.querySelectorAll('.elements, .types');
    
    sections.forEach(section => {
        const filterContainer = document.createElement('div');
        filterContainer.className = 'filter-container';
        filterContainer.innerHTML = `
            <div class="quick-filters">
                <button class="filter-btn active" data-filter="all">All</button>
                <button class="filter-btn" data-filter="required">Required</button>
                <button class="filter-btn" data-filter="optional">Optional</button>
                <button class="filter-btn" data-filter="multiple">Multiple</button>
            </div>
        `;
        
        const heading = section.querySelector('h2');
        heading.insertAdjacentElement('afterend', filterContainer);
        
        // Add filter functionality
        const filterButtons = filterContainer.querySelectorAll('.filter-btn');
        filterButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                // Update active button
                filterButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // Filter elements
                const filter = this.getAttribute('data-filter');
                filterByOccurrence(section, filter);
            });
        });
    });
}

function filterByOccurrence(section, filter) {
    const cards = section.querySelectorAll('.element-card');
    
    cards.forEach(card => {
        const occursElement = card.querySelector('.occurs');
        if (!occursElement) {
            card.style.display = filter === 'all' ? '' : 'none';
            return;
        }
        
        const occursText = occursElement.textContent.toLowerCase();
        let show = false;
        
        switch (filter) {
            case 'all':
                show = true;
                break;
            case 'required':
                show = occursText.includes('required');
                break;
            case 'optional':
                show = occursText.includes('optional');
                break;
            case 'multiple':
                show = occursText.includes('multiple');
                break;
        }
        
        card.style.display = show ? '' : 'none';
    });
}

function initializeExpandableElements() {
    // Make element trees expandable/collapsible
    const treeNodes = document.querySelectorAll('.tree-node');
    
    treeNodes.forEach(node => {
        const children = node.querySelectorAll('.tree-node');
        if (children.length > 0) {
            // Add expand/collapse toggle
            const toggle = document.createElement('span');
            toggle.className = 'tree-toggle';
            toggle.textContent = '−';
            toggle.style.cursor = 'pointer';
            toggle.style.marginRight = '0.5rem';
            toggle.style.fontWeight = 'bold';
            toggle.style.color = 'var(--primary-color)';
            
            const firstChild = node.firstElementChild;
            firstChild.insertBefore(toggle, firstChild.firstChild);
            
            toggle.addEventListener('click', function() {
                const isExpanded = this.textContent === '−';
                
                children.forEach(child => {
                    child.style.display = isExpanded ? 'none' : '';
                });
                
                this.textContent = isExpanded ? '+' : '−';
            });
        }
    });
}

function initializeTooltips() {
    // Add tooltips for type links and complex information
    const typeLinks = document.querySelectorAll('a[href*="types/"]');
    
    typeLinks.forEach(link => {
        link.addEventListener('mouseenter', function(e) {
            showTooltip(e, this.textContent);
        });
        
        link.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event, content) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = content;
    tooltip.style.cssText = `
        position: absolute;
        background: var(--text-color);
        color: white;
        padding: 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        z-index: 1000;
        pointer-events: none;
        max-width: 200px;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = tooltip.getBoundingClientRect();
    tooltip.style.left = (event.pageX - rect.width / 2) + 'px';
    tooltip.style.top = (event.pageY - rect.height - 10) + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Utility functions for dynamic content
function createElementTree(element, container) {
    const treeHtml = generateTreeHTML(element);
    container.innerHTML = treeHtml;
    initializeExpandableElements();
}

function generateTreeHTML(element, depth = 0) {
    const indent = '  '.repeat(depth);
    let html = `${indent}<div class="tree-node">`;
    html += `<span class="tree-element">${element.name}</span>`;
    
    if (element.type) {
        html += ` <span class="tree-type">: ${element.type}</span>`;
    }
    
    if (element.min_occurs || element.max_occurs) {
        html += ` <span class="tree-occurs">[${element.min_occurs || '1'}..${element.max_occurs || '1'}]</span>`;
    }
    
    if (element.children && element.children.length > 0) {
        element.children.forEach(child => {
            html += generateTreeHTML(child, depth + 1);
        });
    }
    
    html += '</div>';
    return html;
}

// Export functions for use in other scripts
window.XSDVisualization = {
    filterElements,
    createElementTree,
    generateTreeHTML
};
