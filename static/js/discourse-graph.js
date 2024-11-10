class DiscourseGraph {
    constructor(container) {
        this.container = container;
        this.width = container.offsetWidth;
        this.height = container.offsetHeight;
        
        // Enhanced color scheme and node configurations
        this.config = {
            nodes: {
                question: { color: '#4e79a7', radius: 12, label: 'Research Question', scrollClass: 'research-question' },
                claim: { color: '#f28e2c', radius: 8, label: 'Claim', scrollClass: 'claim' },
                evidence: { color: '#59a14f', radius: 6, label: 'Evidence', scrollClass: 'evidence' },
                source: { color: '#76b7b2', radius: 7, label: 'Source', scrollClass: 'source' }
            },
            edges: {
                supports: { color: '#86cb92', label: 'Supports' },
                contradicts: { color: '#e15759', label: 'Contradicts' },
                addresses: { color: '#76b7b2', label: 'Addresses' }
            }
        };
        
        this.simulation = d3.forceSimulation()
            .force('link', d3.forceLink().id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2));
    }
    
    addLegend(svg) {
        const legend = svg.append('g')
            .attr('class', 'legend')
            .attr('transform', `translate(20, 20)`);

        // Node type legend
        const nodeTypes = Object.entries(this.config.nodes);
        nodeTypes.forEach(([type, config], i) => {
            const g = legend.append('g')
                .attr('transform', `translate(0, ${i * 25})`);
                
            g.append('circle')
                .attr('r', config.radius)
                .attr('fill', config.color);
                
            g.append('text')
                .attr('x', 20)
                .attr('y', 5)
                .text(config.label);
        });

        // Edge type legend
        const edgeTypes = Object.entries(this.config.edges);
        edgeTypes.forEach(([type, config], i) => {
            const g = legend.append('g')
                .attr('transform', `translate(150, ${i * 25})`);
                
            g.append('line')
                .attr('x1', 0)
                .attr('x2', 30)
                .attr('stroke', config.color)
                .attr('stroke-width', 2);
                
            g.append('text')
                .attr('x', 40)
                .attr('y', 5)
                .text(config.label);
        });
    }
    
    render(data) {
        const svg = d3.select(this.container)
            .append('svg')
            .attr('width', this.width)
            .attr('height', this.height);
            
        // Add zoom behavior
        const g = svg.append('g');
        svg.call(d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            }));
            
        // Add legend
        this.addLegend(svg);
            
        // Create arrow markers
        svg.append('defs').selectAll('marker')
            .data(Object.entries(this.config.edges))
            .enter().append('marker')
            .attr('id', d => d[0])
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 15)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', d => d[1].color);
            
        // Draw edges
        const link = g.append('g')
            .selectAll('line')
            .data(data.edges)
            .enter().append('line')
            .attr('stroke', d => this.config.edges[d.type].color)
            .attr('stroke-width', 2)
            .attr('marker-end', d => `url(#${d.type})`);
            
        // Draw nodes
        const node = g.append('g')
            .selectAll('g')
            .data(data.nodes)
            .enter().append('g')
            .call(d3.drag()
                .on('start', this.dragstarted.bind(this))
                .on('drag', this.dragged.bind(this))
                .on('end', this.dragended.bind(this)))
            .on('click', (event, d) => this.handleNodeClick(d))
            .style('cursor', 'pointer');
                
        // Add circles for nodes
        node.append('circle')
            .attr('r', d => this.config.nodes[d.type].radius)
            .attr('fill', d => this.config.nodes[d.type].color);
            
        // Add labels for nodes
        node.append('text')
            .attr('dx', 12)
            .attr('dy', 4)
            .text(d => this.truncateText(d.label, 30));
            
        // Add tooltips
        node.append('title')
            .text(d => `${this.config.nodes[d.type].label}\n${d.label}\nFrom: ${d.paper}`);
            
        // Update simulation
        this.simulation
            .nodes(data.nodes)
            .on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                    
                node
                    .attr('transform', d => `translate(${d.x},${d.y})`);
            });
            
        this.simulation.force('link')
            .links(data.edges);
    }
    
    truncateText(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    dragstarted(event) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }
    
    dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }
    
    dragended(event) {
        if (!event.active) this.simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
    
    handleNodeClick(d) {
        // Create a unique identifier for the content based on the node data
        const nodeText = d.label;
        const paperName = d.paper;
        
        // Find all elements that might contain this text
        const elements = document.querySelectorAll(`.result, .cross-reference`);
        
        for (const element of elements) {
            if (element.textContent.includes(nodeText) && 
                element.textContent.includes(paperName)) {
                // Found the matching element, scroll to it
                element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                
                // Add highlight effect
                element.classList.add('highlight');
                setTimeout(() => {
                    element.classList.remove('highlight');
                }, 2000);
                
                break;
            }
        }
    }
}