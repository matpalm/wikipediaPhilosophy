import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;

public class DistanceToPhilosophy {
  
  private TokenDictionary tokenDictionary = new TokenDictionary();  
  private final String startNode, edgesFile;
  
  private Set<Integer> nodes = new HashSet<Integer>();
  private Map<Integer,List<Integer>> edges = new HashMap<Integer,List<Integer>>();
  
  public static void main(String args[]) throws IOException {
  	if (args.length != 2) {
  		throw new RuntimeException("DistanceToPhilosophy <startNode> <edgesFile>");
  	}	
    new DistanceToPhilosophy(args).go();
  }
  
  public DistanceToPhilosophy(String[] args) {
    this.startNode = args[0];
    this.edgesFile = args[1];
  }
  
  public void go() throws IOException {
    parseEdgesFile();
    breadthFirstWalk();    
  }
  
  private void parseEdgesFile() throws FileNotFoundException, IOException {
    System.err.println(new Date()+" parseEdgesFile: reading from "+edgesFile);
    BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(edgesFile)));
    int linesProcessed=0;
    
    // first read from file and just convert to idx    
    String next;    
    while((next=reader.readLine())!=null) {     
      String[] cols = next.split("\t");      
      int fromNode = tokenDictionary.idxForToken(cols[1]);
      int toNode = tokenDictionary.idxForToken(cols[0]);      
      
      nodes.add(fromNode);
      nodes.add(toNode);
      
      // build edges structure
      if (edges.containsKey(fromNode)) {
        List<Integer> outboundEdges = edges.get(fromNode);
        if (outboundEdges.contains(toNode)) {
          System.err.println(new Date()+" already an edge from "+fromNode+
              " ("+tokenDictionary.idxToToken.get(fromNode)+") to "+toNode+" ("+tokenDictionary.idxToToken.get(toNode)+")");
        } 
        else {
          outboundEdges.add(toNode);
        }         
      }
      else {        
        List<Integer> newSetOfEdges = new ArrayList<Integer>();
        newSetOfEdges.add(toNode);
        edges.put(fromNode, newSetOfEdges);
      }      
      
      if (++linesProcessed%100000==0) {
        System.err.println(new Date()+" parseEdgesFile:"+
            " linesProcessed="+linesProcessed+            
            " idxToToken.size="+tokenDictionary.idxToToken.size());
      }
    }
    if (!tokenDictionary.tokenToIdx.containsKey(startNode)) {
      throw new RuntimeException("after parsing stdin never saw starting node ["+startNode+"]");
    }
    reader.close();
    
  }

  private void breadthFirstWalk() {
    Queue<Integer> boundary = new LinkedList<Integer>();
    Set<Integer> visitedNodes = new HashSet<Integer>();    
    Set<Integer> unvisitedNodes = new HashSet<Integer>(nodes);

    int start = tokenDictionary.tokenToIdx.get(startNode);
    boundary.add(start);
    visitedNodes.add(start);
    unvisitedNodes.remove(start);
    
    int distance = 0;    
    while(boundary.size() != 0) {
      Queue<Integer> frontier = new LinkedList<Integer>();
      for(int boundaryNode : boundary) {
        System.out.println("FINAL "+tokenDictionary.idxToToken.get(boundaryNode) + "\t" + distance);
        visitedNodes.add(boundaryNode);
        unvisitedNodes.remove(boundaryNode);
        
        if (edges.containsKey(boundaryNode)) {
          for (int outboundNode : edges.get(boundaryNode)) {
            if (unvisitedNodes.contains(outboundNode)) {
              frontier.add(outboundNode);
            }
          }
        }        
      }
      System.err.println("distance="+distance+" frontier size "+frontier.size()+
          " visitedNodes.size="+visitedNodes.size()+
          " unvisitedNodes.size="+unvisitedNodes.size());      
      distance++;
      boundary = frontier;      
    }
        
    for (int node : unvisitedNodes) {
      System.out.println("didnt visit "+tokenDictionary.idxToToken.get(node));
    }
    
  }
  
}

